import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.storage import open_stream, save_upload
from app.models.db_models import Video
from app.models.schemas import VideoImportRequest, VideoOut
from app.workers.celery_app import enqueue_task

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/upload", response_model=VideoOut)
async def upload_video(
    file: UploadFile,
    owner_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    key = f"raw/{uuid.uuid4()}-{file.filename}"
    save_upload(key, file.file)

    video = Video(
        owner_id=owner_id,
        title=file.filename or "Untitled lecture",
        s3_key=key,
        status="uploaded",
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)

    enqueue_task("app.workers.pipeline.process_video", [video.id])
    return video


@router.post("/import-url", response_model=VideoOut)
async def import_video_from_url(
    body: VideoImportRequest,
    owner_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Download a video from a URL (YouTube, Vimeo, direct .mp4 link), then process it."""
    url = body.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    video = Video(
        owner_id=owner_id,
        title="Downloading…",
        s3_key="",
        source_url=url,
        status="downloading",
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)

    enqueue_task("app.workers.pipeline.import_from_url", [video.id, url])
    return video


@router.get("", response_model=list[VideoOut])
async def list_videos(owner_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.owner_id == owner_id))
    return result.scalars().all()


@router.get("/{video_id}", response_model=VideoOut)
async def get_video(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.get("/{video_id}/stream")
async def stream_video(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if not video.s3_key:
        raise HTTPException(status_code=409, detail="Video is still downloading")

    body, media_type = open_stream(video.s3_key)
    return StreamingResponse(body, media_type=media_type, headers={"Accept-Ranges": "bytes"})
