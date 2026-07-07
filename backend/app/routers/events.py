import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.db_models import ProcessingEvent, Video

router = APIRouter(prefix="/events", tags=["events"])

STEP_PROGRESS = {
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
}


@router.get("/videos/{video_id}/stream")
async def video_processing_stream(video_id: str):
    async with AsyncSessionLocal() as db:
        video = await db.get(Video, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

    async def event_generator():
        last_progress = -1
        while True:
            async with AsyncSessionLocal() as db:
                video = await db.get(Video, video_id)
                if not video:
                    break
                result = await db.execute(
                    select(ProcessingEvent)
                    .where(ProcessingEvent.video_id == video_id)
                    .order_by(ProcessingEvent.created_at.desc())
                    .limit(1)
                )
                event = result.scalar_one_or_none()
                status = video.status

                if event:
                    payload = {
                        "step": event.step,
                        "message": event.message,
                        "progress": event.progress,
                    }
                else:
                    payload = {
                        "step": status,
                        "message": status.replace("_", " ").title(),
                        "progress": STEP_PROGRESS.get(status, 0),
                    }

                if payload["progress"] != last_progress or status in ("ready", "failed"):
                    yield f"data: {json.dumps(payload)}\n\n"
                    last_progress = payload["progress"]

                if status in ("ready", "failed"):
                    break
            await asyncio.sleep(1.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
