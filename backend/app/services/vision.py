"""Vision summaries via Claude (when API key available) or heuristics."""

import base64
from pathlib import Path

from anthropic import Anthropic

from app.core.config import settings
from app.services.scene_detection import describe_frame


def describe_frame_enhanced(frame_path: Path) -> str:
    heuristic = describe_frame(frame_path)
    if not settings.anthropic_api_key or not frame_path.exists():
        return heuristic

    try:
        image_data = base64.standard_b64encode(frame_path.read_bytes()).decode()
        client = Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=120,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "Describe this lecture frame in one sentence. "
                                "Mention slides, formulas, code, diagrams, or speaker if visible."
                            ),
                        },
                    ],
                }
            ],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        return text.strip() or heuristic
    except Exception:
        return heuristic
