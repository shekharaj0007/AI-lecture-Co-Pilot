import math

from anthropic import Anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.db_models import CourseVideo, TimelineChunk
from app.models.schemas import ChatResponse, Citation
from app.services.embeddings import embed_text
from app.services.hybrid_search import hybrid_rank
from app.services.translate import translate_text


def _anthropic_client() -> Anthropic | None:
    if not settings.anthropic_api_key:
        return None
    return Anthropic(api_key=settings.anthropic_api_key)


async def _retrieve_chunks(db: AsyncSession, video_id: str, query_embedding: list[float], query_text: str, limit: int = 6):
    result = await db.execute(select(TimelineChunk).where(TimelineChunk.video_id == video_id))
    chunks = list(result.scalars().all())
    return hybrid_rank(chunks, query_embedding, query_text, limit=limit)


async def _retrieve_course_chunks(
    db: AsyncSession, course_id: str, query_embedding: list[float], query_text: str, limit: int = 8
):
    result = await db.execute(
        select(TimelineChunk)
        .join(CourseVideo, CourseVideo.video_id == TimelineChunk.video_id)
        .where(CourseVideo.course_id == course_id)
    )
    chunks = list(result.scalars().all())
    return hybrid_rank(chunks, query_embedding, query_text, limit=limit)


def _build_response(chunks: list[TimelineChunk], question: str, target_language: str | None) -> ChatResponse:
    if not chunks:
        return ChatResponse(
            answer="No relevant content found yet. Try again after processing completes.",
            citations=[],
        )

    context = "\n\n".join(
        f"[Video {c.video_id} | {c.start_seconds:.0f}s-{c.end_seconds:.0f}s] "
        f"{c.transcript_text} {c.ocr_text} {c.visual_summary}".strip()
        for c in chunks
    )

    client = _anthropic_client()
    if not client:
        answer = f"Add ANTHROPIC_API_KEY for AI answers. Retrieved {len(chunks)} relevant segment(s)."
    else:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=(
                "You are a lecture assistant. Answer only from the provided excerpts. "
                "Cite timestamps and video references when relevant. Be concise."
            ),
            messages=[{"role": "user", "content": f"Excerpts:\n{context}\n\nQuestion: {question}"}],
        )
        answer = "".join(block.text for block in response.content if block.type == "text")

    if target_language:
        answer = translate_text(answer, target_language)

    return ChatResponse(
        answer=answer,
        citations=[
            Citation(
                start_seconds=c.start_seconds,
                end_seconds=c.end_seconds,
                snippet=c.transcript_text[:160],
                video_id=c.video_id,
            )
            for c in chunks
        ],
    )


async def answer_question(
    db: AsyncSession,
    question: str,
    video_id: str | None = None,
    course_id: str | None = None,
    target_language: str | None = None,
) -> ChatResponse:
    query_embedding = await embed_text(question)

    if course_id:
        chunks = await _retrieve_course_chunks(db, course_id, query_embedding, question)
    elif video_id:
        if settings.is_sqlite:
            chunks = await _retrieve_chunks(db, video_id, query_embedding, question)
        else:
            result = await db.execute(
                select(TimelineChunk)
                .where(TimelineChunk.video_id == video_id)
                .order_by(TimelineChunk.embedding.cosine_distance(query_embedding))
                .limit(6)
            )
            chunks = list(result.scalars().all())
    else:
        return ChatResponse(answer="Provide a video_id or course_id.", citations=[])

    return _build_response(chunks, question, target_language)
