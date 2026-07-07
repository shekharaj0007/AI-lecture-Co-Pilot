"""Auto-generate quizzes and practice exams from lecture content."""

import json

from anthropic import Anthropic

from app.core.config import settings


def generate_quiz_questions(transcript: str, count: int = 8) -> list[dict]:
    if not settings.anthropic_api_key:
        return [
            {
                "question": "What enables auto-generated quizzes?",
                "options": ["ANTHROPIC_API_KEY", "ffmpeg", "Redis", "Docker"],
                "correct_index": 0,
                "explanation": "Add ANTHROPIC_API_KEY to .env for AI quiz generation.",
                "source_seconds": 0,
            }
        ]

    client = Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Create {count} multiple-choice quiz questions from this lecture. "
                    'Return JSON array only: [{"question":"...","options":["A","B","C","D"],'
                    '"correct_index":0,"explanation":"...","source_seconds":0}]\n\n'
                    f"{transcript[:6000]}"
                ),
            }
        ],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end <= start:
        return []
    return json.loads(text[start:end])
