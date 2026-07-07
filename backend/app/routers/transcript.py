from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.db_models import TimelineChunk
from app.models.schemas import TranscriptSegmentOut

router = APIRouter(prefix="/transcript", tags=["transcript"])


@router.get("/{video_id}", response_model=list[TranscriptSegmentOut])
async def get_transcript(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TimelineChunk)
        .where(TimelineChunk.video_id == video_id)
        .order_by(TimelineChunk.start_seconds)
    )
    chunks = result.scalars().all()
    return [
        TranscriptSegmentOut(
            start_seconds=c.start_seconds,
            end_seconds=c.end_seconds,
            speaker=c.speaker,
            text=c.transcript_text,
            ocr_text=c.ocr_text or "",
            chapter_title=c.chapter_title,
        )
        for c in chunks
    ]
