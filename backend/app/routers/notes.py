from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.db_models import Note
from app.models.schemas import NoteOut

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/{video_id}", response_model=list[NoteOut])
async def get_notes(video_id: str, db: AsyncSession = Depends(get_db)):
    """Notes are generated once per chapter during the processing pipeline
    (see app/workers/pipeline.py) — this just reads them back, ordered by
    when they occur in the video."""
    result = await db.execute(
        select(Note).where(Note.video_id == video_id).order_by(Note.start_seconds)
    )
    return result.scalars().all()
