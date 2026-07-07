"""LLM-powered chapter titles from transcript excerpts."""

from anthropic import Anthropic

from app.core.config import settings


def name_chapters(chapters: list[dict], segments: list[dict]) -> list[dict]:
    if not chapters:
        return chapters
    if not settings.anthropic_api_key:
        return chapters

    client = Anthropic(api_key=settings.anthropic_api_key)
    named = []
    for i, chapter in enumerate(chapters):
        excerpt = " ".join(
            seg["text"]
            for seg in segments
            if chapter["start"] <= seg["start"] < chapter["end"]
        )[:1200]
        if not excerpt.strip():
            named.append(chapter)
            continue
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=40,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Give a short chapter title (3-6 words) for lecture section {i + 1}. "
                            f"Transcript excerpt:\n{excerpt}"
                        ),
                    }
                ],
            )
            title = "".join(block.text for block in response.content if block.type == "text").strip()
            named.append({**chapter, "title": title or chapter["title"]})
        except Exception:
            named.append(chapter)
    return named
