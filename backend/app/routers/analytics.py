from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_optional_user
from app.core.db import get_db
from app.models.db_models import QuizAttempt, User, Video
from app.models.schemas import AnalyticsOut

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsOut)
async def user_analytics(
    user: User | None = Depends(get_optional_user),
    owner_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    uid = user.id if user else owner_id or "demo-user"

    total = await db.scalar(select(func.count()).select_from(Video).where(Video.owner_id == uid)) or 0
    ready = await db.scalar(
        select(func.count()).select_from(Video).where(Video.owner_id == uid, Video.status == "ready")
    ) or 0
    attempts = await db.scalar(
        select(func.count()).select_from(QuizAttempt).where(QuizAttempt.user_id == uid)
    ) or 0
    avg_score = await db.scalar(
        select(func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total)).where(
            QuizAttempt.user_id == uid, QuizAttempt.total > 0
        )
    )
    study_seconds = await db.scalar(
        select(func.sum(Video.duration_seconds)).where(Video.owner_id == uid, Video.status == "ready")
    ) or 0

    return AnalyticsOut(
        total_videos=total,
        ready_videos=ready,
        total_flashcards_reviewed=0,
        total_quiz_attempts=attempts,
        average_quiz_score=float(avg_score or 0),
        study_hours=round(float(study_seconds) / 3600, 1),
    )
