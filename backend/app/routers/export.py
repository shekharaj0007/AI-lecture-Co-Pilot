from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.db_models import Note, TimelineChunk, Video

router = APIRouter(prefix="/export", tags=["export"])


def _format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


@router.get("/{video_id}/transcript.srt")
async def export_srt(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TimelineChunk)
        .where(TimelineChunk.video_id == video_id)
        .order_by(TimelineChunk.start_seconds)
    )
    chunks = result.scalars().all()
    lines = []
    for i, chunk in enumerate(chunks, 1):
        lines.append(str(i))
        lines.append(
            f"{_format_srt_time(chunk.start_seconds)} --> {_format_srt_time(chunk.end_seconds)}"
        )
        lines.append(chunk.transcript_text.strip())
        lines.append("")
    return PlainTextResponse("\n".join(lines), media_type="application/x-subrip")


@router.get("/{video_id}/notes.md")
async def export_notes_md(video_id: str, db: AsyncSession = Depends(get_db)):
    video = await db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    result = await db.execute(select(Note).where(Note.video_id == video_id))
    notes = result.scalars().all()
    parts = [f"# {video.title}\n"]
    for note in notes:
        parts.append(f"\n## {note.chapter_title}\n\n{note.content_markdown}\n")
    return PlainTextResponse("\n".join(parts), media_type="text/markdown")


@router.get("/{video_id}/anki.csv")
async def export_anki(video_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.db_models import Flashcard

    result = await db.execute(select(Flashcard).where(Flashcard.video_id == video_id))
    cards = result.scalars().all()
    lines = ["front,back,tags"]
    for card in cards:
        front = card.question.replace('"', '""')
        back = card.answer.replace('"', '""')
        lines.append(f'"{front}","{back}","lecture-copilot"')
    return Response(
        "\n".join(lines),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{video_id}-anki.csv"'},
    )
