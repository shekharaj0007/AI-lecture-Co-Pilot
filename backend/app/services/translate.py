"""Multilingual translation for transcript and Q&A."""

from anthropic import Anthropic

from app.core.config import settings


def translate_text(text: str, target_language: str) -> str:
    if not text.strip() or target_language.lower() in ("en", "english"):
        return text
    if not settings.anthropic_api_key:
        return f"[Set ANTHROPIC_API_KEY to translate to {target_language}]\n{text}"

    client = Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Translate the following lecture text to {target_language}. "
                    f"Preserve meaning and technical terms.\n\n{text}"
                ),
            }
        ],
    )
    return "".join(block.text for block in response.content if block.type == "text")
