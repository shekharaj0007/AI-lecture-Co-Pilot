"""Processing event log for SSE live progress."""

from sqlalchemy import select

from app.core.sync_db import SyncSessionLocal
from app.models.db_models import ProcessingEvent


def emit_event(video_id: str, step: str, message: str, progress: int) -> None:
    with SyncSessionLocal() as db:
        db.add(
            ProcessingEvent(
                video_id=video_id,
                step=step,
                message=message,
                progress=max(0, min(100, progress)),
            )
        )
        db.commit()


def latest_event(video_id: str) -> ProcessingEvent | None:
    with SyncSessionLocal() as db:
        result = db.execute(
            select(ProcessingEvent)
            .where(ProcessingEvent.video_id == video_id)
            .order_by(ProcessingEvent.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
