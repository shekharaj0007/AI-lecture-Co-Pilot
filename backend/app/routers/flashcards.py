from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.db_models import Flashcard
from app.models.schemas import FlashcardOut, FlashcardReview

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.get("/{video_id}/due", response_model=list[FlashcardOut])
async def get_due_flashcards(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Flashcard)
        .where(Flashcard.video_id == video_id, Flashcard.due_at <= datetime.utcnow())
        .order_by(Flashcard.due_at)
    )
    return result.scalars().all()


@router.post("/review")
async def review_flashcard(review: FlashcardReview, db: AsyncSession = Depends(get_db)):
    """
    Standard SM-2 spaced repetition update. `quality` is a 0-5 self-rating
    of recall (0 = total blackout, 5 = perfect). Reschedules `due_at`
    accordingly — this is what turns a static flashcard deck into spaced
    review.
    """
    result = await db.execute(select(Flashcard).where(Flashcard.id == review.flashcard_id))
    card = result.scalar_one()

    if review.quality < 3:
        card.repetitions = 0
        card.interval_days = 1
    else:
        card.repetitions += 1
        if card.repetitions == 1:
            card.interval_days = 1
        elif card.repetitions == 2:
            card.interval_days = 6
        else:
            card.interval_days = round(card.interval_days * card.ease_factor)

        card.ease_factor = max(
            1.3,
            card.ease_factor + (0.1 - (5 - review.quality) * (0.08 + (5 - review.quality) * 0.02)),
        )

    card.due_at = datetime.utcnow() + timedelta(days=card.interval_days)
    await db.commit()
    return {"next_due": card.due_at, "interval_days": card.interval_days}
