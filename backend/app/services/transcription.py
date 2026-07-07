"""Transcription via faster-whisper (local) or Groq API (hosted)."""

from pathlib import Path

import httpx

from app.core.config import settings
from app.services.video_media import extract_audio


def transcribe_video(video_path: Path) -> tuple[list[dict], float]:
    from app.services.video_media import probe_duration

    duration = probe_duration(video_path)

    if settings.groq_api_key:
        return _transcribe_groq(video_path), duration

    try:
        return _transcribe_faster_whisper(video_path), duration
    except ImportError:
        return _placeholder_segments(duration), duration


def _transcribe_groq(video_path: Path) -> list[dict]:
    audio_path = extract_audio(video_path)
    with open(audio_path, "rb") as audio_file:
        response = httpx.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            data={"model": "whisper-large-v3", "response_format": "verbose_json"},
            files={"file": ("audio.wav", audio_file, "audio/wav")},
            timeout=600,
        )
    response.raise_for_status()
    payload = response.json()
    return [
        {
            "start": float(item["start"]),
            "end": float(item["end"]),
            "text": item["text"].strip(),
            "speaker": None,
        }
        for item in payload.get("segments", [])
        if item.get("text", "").strip()
    ]


def _transcribe_faster_whisper(video_path: Path) -> list[dict]:
    from faster_whisper import WhisperModel

    audio_path = extract_audio(video_path)
    model = WhisperModel(settings.whisper_model, device="cpu", compute_type="int8")
    segments_iter, _ = model.transcribe(str(audio_path), beam_size=5, vad_filter=True)

    segments = []
    for seg in segments_iter:
        text = seg.text.strip()
        if not text:
            continue
        segments.append(
            {
                "start": float(seg.start),
                "end": float(seg.end),
                "text": text,
                "speaker": None,
            }
        )
    return segments


def _placeholder_segments(duration: float) -> list[dict]:
    segment_count = max(1, int(duration // 60) + 1)
    window = duration / segment_count
    return [
        {
            "start": i * window,
            "end": min((i + 1) * window, duration),
            "text": (
                f"Lecture segment {i + 1}. Install ffmpeg and run "
                f"'pip install faster-whisper' for real transcription."
            ),
            "speaker": None,
        }
        for i in range(segment_count)
    ]
