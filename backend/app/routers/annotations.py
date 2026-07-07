from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, get_optional_user
from app.core.db import get_db
from app.models.db_models import Annotation, User
from app.models.schemas import AnnotationCreate, AnnotationOut
from app.services.audit import log_action

router = APIRouter(prefix="/annotations", tags=["annotations"])


@router.get("/{video_id}", response_model=list[AnnotationOut])
async def list_annotations(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Annotation)
        .where(Annotation.video_id == video_id)
        .order_by(Annotation.start_seconds)
    )
    return result.scalars().all()


@router.post("", response_model=AnnotationOut)
async def create_annotation(
    body: AnnotationCreate,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = user.id if user else "demo-user"
    annotation = Annotation(
        video_id=body.video_id,
        user_id=user_id,
        start_seconds=body.start_seconds,
        end_seconds=body.end_seconds,
        annotation_type=body.annotation_type,
        text=body.text,
    )
    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)
    await log_action(db, user_id, "create", "annotation", annotation.id)
    return annotation


@router.delete("/{annotation_id}")
async def delete_annotation(
    annotation_id: str,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    annotation = await db.get(Annotation, annotation_id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    await db.delete(annotation)
    await db.commit()
    await log_action(db, user.id if user else None, "delete", "annotation", annotation_id)
    return {"ok": True}
