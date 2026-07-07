import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_optional_user
from app.core.db import get_db
from app.models.db_models import Quiz, QuizAttempt, QuizQuestion, User
from app.models.schemas import QuizOut, QuizQuestionOut, QuizSubmitRequest, QuizSubmitResponse
from app.services.quiz_generator import generate_quiz_questions

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("/{video_id}", response_model=QuizOut | None)
async def get_quiz(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quiz).where(Quiz.video_id == video_id).limit(1))
    quiz = result.scalar_one_or_none()
    if not quiz:
        return None
    q_result = await db.execute(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id))
    questions = q_result.scalars().all()
    return QuizOut(
        id=quiz.id,
        title=quiz.title,
        questions=[
            QuizQuestionOut(
                id=q.id,
                question=q.question,
                options=json.loads(q.options),
                source_seconds=q.source_seconds,
            )
            for q in questions
        ],
    )


@router.post("/{video_id}/generate", response_model=QuizOut)
async def generate_quiz(video_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.db_models import TimelineChunk

    result = await db.execute(
        select(TimelineChunk)
        .where(TimelineChunk.video_id == video_id)
        .order_by(TimelineChunk.start_seconds)
    )
    chunks = result.scalars().all()
    transcript = "\n".join(f"[{c.start_seconds:.0f}s] {c.transcript_text}" for c in chunks[:50])
    raw_questions = generate_quiz_questions(transcript)

    existing = await db.execute(select(Quiz).where(Quiz.video_id == video_id))
    quiz = existing.scalar_one_or_none()
    if not quiz:
        quiz = Quiz(video_id=video_id, title="Practice Quiz")
        db.add(quiz)
        await db.flush()
    else:
        old_q = await db.execute(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id))
        for q in old_q.scalars().all():
            await db.delete(q)

    questions_out = []
    for item in raw_questions:
        q = QuizQuestion(
            quiz_id=quiz.id,
            question=item["question"],
            options=json.dumps(item["options"]),
            correct_index=item["correct_index"],
            explanation=item.get("explanation", ""),
            source_seconds=item.get("source_seconds"),
        )
        db.add(q)
        await db.flush()
        questions_out.append(
            QuizQuestionOut(
                id=q.id,
                question=q.question,
                options=item["options"],
                source_seconds=q.source_seconds,
            )
        )

    await db.commit()
    return QuizOut(id=quiz.id, title=quiz.title, questions=questions_out)


@router.post("/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    body: QuizSubmitRequest,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(QuizQuestion).where(QuizQuestion.quiz_id == body.quiz_id))
    questions = list(result.scalars().all())
    results = []
    score = 0
    for i, question in enumerate(questions):
        chosen = body.answers[i] if i < len(body.answers) else -1
        correct = chosen == question.correct_index
        if correct:
            score += 1
        results.append(
            {
                "question_id": question.id,
                "correct": correct,
                "correct_index": question.correct_index,
                "explanation": question.explanation,
            }
        )

    user_id = user.id if user else "demo-user"
    db.add(
        QuizAttempt(
            user_id=user_id,
            quiz_id=body.quiz_id,
            score=score,
            total=len(questions),
        )
    )
    await db.commit()
    return QuizSubmitResponse(score=score, total=len(questions), results=results)
