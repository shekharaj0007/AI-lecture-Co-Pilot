import hashlib
import math

import httpx

from app.core.config import settings

EMBEDDING_DIM = 1536


def _deterministic_embedding(text: str) -> list[float]:
    """Dev fallback: hash text into a unit-normalized 1536-d vector."""
    digest = hashlib.sha512(text.encode()).digest()
    values: list[float] = []
    while len(values) < EMBEDDING_DIM:
        for i in range(0, len(digest), 4):
            chunk = digest[i : i + 4]
            if len(chunk) < 4:
                break
            values.append(int.from_bytes(chunk, "big") / 2**32)
            if len(values) == EMBEDDING_DIM:
                break
        digest = hashlib.sha512(digest).digest()

    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


async def embed_text(text: str) -> list[float]:
    if settings.voyage_api_key:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {settings.voyage_api_key}"},
                json={"input": text, "model": "voyage-3"},
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]

    return _deterministic_embedding(text)


def embed_text_sync(text: str) -> list[float]:
    if settings.voyage_api_key:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {settings.voyage_api_key}"},
                json={"input": text, "model": "voyage-3"},
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]

    return _deterministic_embedding(text)
