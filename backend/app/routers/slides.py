from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.models.db_models import Slide
from app.models.schemas import SlideOut, TranslateRequest

router = APIRouter(prefix="/slides", tags=["slides"])


@router.get("/{video_id}", response_model=list[SlideOut])
async def list_slides(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Slide).where(Slide.video_id == video_id).order_by(Slide.start_seconds)
    )
    slides = result.scalars().all()
    return [
        SlideOut(
            id=s.id,
            start_seconds=s.start_seconds,
            title=s.title,
            image_url=f"/slides/{video_id}/image/{s.id}",
            ocr_text=s.ocr_text,
        )
        for s in slides
    ]


@router.get("/{video_id}/image/{slide_id}")
async def get_slide_image(slide_id: str, db: AsyncSession = Depends(get_db)):
    from fastapi.responses import FileResponse

    slide = await db.get(Slide, slide_id)
    if not slide:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Slide not found")
    path = settings.uploads_dir.parent / slide.image_path
    return FileResponse(path)


@router.post("/translate")
async def translate_content(body: TranslateRequest):
    from app.services.translate import translate_text

    return {"translated": translate_text(body.text, body.target_language)}
