"""
End-to-end video processing pipeline.

Flow matches the architecture diagram:
  Whisper → CLIP/scene detection → OCR → diarization → fused timeline → vector index → notes/flashcards
"""

import json
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic
from sqlalchemy import delete, select

from app.core.config import settings
from app.core.storage import download_to_path, save_file_from_path
from app.core.sync_db import SyncSessionLocal
from app.models.db_models import Flashcard, Note, Quiz, QuizQuestion, Slide, TimelineChunk, Video
from app.services.diarization import assign_speakers
from app.services.embeddings import embed_text_sync
from app.services.ocr import ocr_for_chapters
from app.services.processing_events import emit_event
from app.services.quiz_generator import generate_quiz_questions
from app.services.scene_detection import detect_scenes
from app.services.slides import extract_slides
from app.services.smart_chapters import name_chapters
from app.services.transcription import transcribe_video
from app.services.video_download import _safe_filename, download_video_url
from app.services.video_media import extract_frame_at, probe_duration
from app.services.vision import describe_frame_enhanced
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.pipeline.import_from_url")
def import_from_url(video_id: str, url: str):
    tmp_dir: Path | None = None
    try:
        _set_status(video_id, "downloading")
        video_path, title, tmp_dir = download_video_url(url)
        ext = video_path.suffix or ".mp4"
        key = f"raw/{uuid.uuid4()}-{_safe_filename(title)}{ext}"
        save_file_from_path(key, video_path)

        with SyncSessionLocal() as db:
            video = db.execute(select(Video).where(Video.id == video_id)).scalar_one()
            video.s3_key = key
            video.title = title[:200]
            video.source_url = url
            video.status = "uploaded"
            db.commit()

        process_video.run(video_id)
    except Exception as exc:
        _set_status(video_id, "failed")
        import logging
        logging.getLogger(__name__).exception("Import failed: %s", exc)
        raise
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)


@celery_app.task(name="app.workers.pipeline.process_video")
def process_video(video_id: str):
    tmp_dir = Path(tempfile.mkdtemp(prefix="lecture-copilot-"))
    try:
        video_path = tmp_dir / "video.mp4"
        download_to_path(_get_s3_key(video_id), video_path)
        duration = probe_duration(video_path)

        _set_status(video_id, "transcribing")
        segments = transcribe_video(video_path)[0]

        _set_status(video_id, "detecting_scenes")
        chapters = detect_scenes(video_path, duration)
        chapters = name_chapters(chapters, segments)

        _set_status(video_id, "extracting_text")
        ocr_segments = ocr_for_chapters(video_path, chapters, video_id)
        slide_data = extract_slides(video_path, video_id, chapters)
        _store_slides(video_id, slide_data, ocr_segments)

        _set_status(video_id, "diarizing")
        segments = assign_speakers(segments)

        _set_status(video_id, "fusing_timeline")
        chunks = _fuse_timeline(video_path, video_id, segments, chapters, ocr_segments)

        _set_status(video_id, "indexing")
        _embed_and_store(video_id, chunks)

        _set_status(video_id, "generating_notes_and_flashcards")
        _generate_notes(video_id, chunks)
        _generate_flashcards(video_id, chunks)
        _generate_quiz(video_id, chunks)

        _set_status(video_id, "ready", duration_seconds=duration)
    except Exception:
        _set_status(video_id, "failed")
        raise
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _get_s3_key(video_id: str) -> str:
    with SyncSessionLocal() as db:
        video = db.execute(select(Video).where(Video.id == video_id)).scalar_one()
        return video.s3_key


def _set_status(video_id: str, status: str, duration_seconds: float | None = None) -> None:
    emit_event(video_id, status, status.replace("_", " ").title(), _progress_for_status(status))
    with SyncSessionLocal() as db:
        video = db.execute(select(Video).where(Video.id == video_id)).scalar_one()
        video.status = status
        if duration_seconds is not None:
            video.duration_seconds = duration_seconds
        db.commit()


def _progress_for_status(status: str) -> int:
    return {
        "downloading": 10,
        "uploaded": 15,
        "transcribing": 25,
        "detecting_scenes": 40,
        "extracting_text": 55,
        "diarizing": 65,
        "fusing_timeline": 75,
        "indexing": 85,
        "generating_notes_and_flashcards": 95,
        "ready": 100,
        "failed": 100,
    }.get(status, 0)


def _ocr_for_segment(ocr_segments: list[dict], start: float, end: float) -> str:
    texts = []
    for item in ocr_segments:
        ocr_start = item["start"]
        ocr_end = item.get("end", ocr_start + 1)
        if ocr_start <= end and ocr_end >= start:
            texts.append(item.get("text", ""))
    return " ".join(texts).strip()


def _fuse_timeline(
    video_path: Path,
    video_id: str,
    segments: list[dict],
    chapters: list[dict],
    ocr_segments: list[dict],
) -> list[dict]:
    frames_root = settings.frames_dir / video_id
    chunks = []

    for segment in segments:
        chapter_title = _chapter_for_time(chapters, segment["start"])
        frame_path = frames_root / f"seg_{int(segment['start'])}.jpg"
        extract_frame_at(video_path, segment["start"], frame_path)
        visual = describe_frame_enhanced(frame_path) if frame_path.exists() else ""

        chunks.append(
            {
                "start_seconds": segment["start"],
                "end_seconds": segment["end"],
                "speaker": segment.get("speaker"),
                "transcript_text": segment["text"],
                "ocr_text": _ocr_for_segment(ocr_segments, segment["start"], segment["end"]),
                "chapter_title": chapter_title,
                "visual_summary": visual,
            }
        )
    return chunks


def _chapter_for_time(chapters: list[dict], seconds: float) -> str | None:
    for chapter in chapters:
        if chapter["start"] <= seconds < chapter["end"]:
            return chapter["title"]
    return chapters[-1]["title"] if chapters else None


def _embed_and_store(video_id: str, chunks: list[dict]) -> None:
    with SyncSessionLocal() as db:
        db.execute(delete(TimelineChunk).where(TimelineChunk.video_id == video_id))
        for chunk in chunks:
            combined = " ".join(
                filter(
                    None,
                    [
                        chunk["transcript_text"],
                        chunk.get("ocr_text"),
                        chunk.get("visual_summary"),
                    ],
                )
            ).strip()
            db.add(
                TimelineChunk(
                    video_id=video_id,
                    start_seconds=chunk["start_seconds"],
                    end_seconds=chunk["end_seconds"],
                    speaker=chunk.get("speaker"),
                    transcript_text=chunk["transcript_text"],
                    ocr_text=chunk.get("ocr_text", ""),
                    chapter_title=chunk.get("chapter_title"),
                    visual_summary=chunk.get("visual_summary", ""),
                    embedding=embed_text_sync(combined),
                )
            )
        db.commit()


def _generate_notes(video_id: str, chunks: list[dict]) -> None:
    by_chapter: dict[str, list[dict]] = {}
    for chunk in chunks:
        title = chunk.get("chapter_title") or "Overview"
        by_chapter.setdefault(title, []).append(chunk)

    with SyncSessionLocal() as db:
        db.execute(delete(Note).where(Note.video_id == video_id))
        for title, chapter_chunks in by_chapter.items():
            transcript = "\n".join(
                f"[{c['start_seconds']:.0f}s] ({c.get('speaker', '?')}) {c['transcript_text']}"
                + (f" | on-screen: {c['ocr_text']}" if c.get("ocr_text") else "")
                for c in chapter_chunks
            )
            db.add(
                Note(
                    video_id=video_id,
                    chapter_title=title,
                    start_seconds=chapter_chunks[0]["start_seconds"],
                    content_markdown=_llm_notes(title, transcript),
                )
            )
        db.commit()


def _generate_flashcards(video_id: str, chunks: list[dict]) -> None:
    transcript = "\n".join(
        f"[{c['start_seconds']:.0f}s] {c['transcript_text']}" for c in chunks[:40]
    )
    cards = _llm_flashcards(transcript)

    with SyncSessionLocal() as db:
        db.execute(delete(Flashcard).where(Flashcard.video_id == video_id))
        for card in cards:
            db.add(
                Flashcard(
                    video_id=video_id,
                    question=card["question"],
                    answer=card["answer"],
                    source_seconds=card.get("source_seconds"),
                    due_at=datetime.utcnow(),
                )
            )
        db.commit()


def _llm_notes(chapter_title: str, transcript: str) -> str:
    if not settings.anthropic_api_key:
        return (
            f"## {chapter_title}\n\n"
            "- Add `ANTHROPIC_API_KEY` to `.env` for AI-generated notes.\n\n"
            f"**Transcript excerpt:**\n\n{transcript[:800]}"
        )

    client = Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Write concise markdown lecture notes for '{chapter_title}'. "
                    f"Use bullet points and highlight key definitions.\n\n{transcript}"
                ),
            }
        ],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def _llm_flashcards(transcript: str) -> list[dict]:
    if not settings.anthropic_api_key:
        return [
            {
                "question": "What API key enables auto-generated flashcards?",
                "answer": "ANTHROPIC_API_KEY in the .env file.",
                "source_seconds": 0,
            }
        ]

    client = Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        messages=[
            {
                "role": "user",
                "content": (
                    "Create 5 study flashcards from this lecture transcript. "
                    'Return JSON array only: [{"question":"...","answer":"...","source_seconds":0}]\n\n'
                    f"{transcript}"
                ),
            }
        ],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end <= start:
        return []
    return json.loads(text[start:end])


def _store_slides(video_id: str, slide_data: list[dict], ocr_segments: list[dict]) -> None:
    with SyncSessionLocal() as db:
        db.execute(delete(Slide).where(Slide.video_id == video_id))
        for slide in slide_data:
            ocr = _ocr_for_segment(ocr_segments, slide["start_seconds"], slide["start_seconds"] + 5)
            db.add(
                Slide(
                    video_id=video_id,
                    start_seconds=slide["start_seconds"],
                    title=slide["title"],
                    image_path=slide["image_path"],
                    ocr_text=ocr,
                )
            )
        db.commit()


def _generate_quiz(video_id: str, chunks: list[dict]) -> None:
    transcript = "\n".join(
        f"[{c['start_seconds']:.0f}s] {c['transcript_text']}" for c in chunks[:50]
    )
    raw = generate_quiz_questions(transcript)
    with SyncSessionLocal() as db:
        existing = db.execute(select(Quiz).where(Quiz.video_id == video_id)).scalar_one_or_none()
        if existing:
            db.execute(delete(QuizQuestion).where(QuizQuestion.quiz_id == existing.id))
            quiz = existing
        else:
            quiz = Quiz(video_id=video_id, title="Practice Quiz")
            db.add(quiz)
            db.flush()
        for item in raw:
            db.add(
                QuizQuestion(
                    quiz_id=quiz.id,
                    question=item["question"],
                    options=json.dumps(item["options"]),
                    correct_index=item["correct_index"],
                    explanation=item.get("explanation", ""),
                    source_seconds=item.get("source_seconds"),
                )
            )
        db.commit()
