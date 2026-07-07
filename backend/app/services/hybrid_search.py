"""Hybrid retrieval: cosine vector similarity + BM25 keyword scoring."""

import math
import re
from collections import Counter

from app.models.db_models import TimelineChunk


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _bm25_scores(query: str, documents: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    if not documents:
        return []
    tokenized = [_tokenize(doc) for doc in documents]
    query_tokens = _tokenize(query)
    if not query_tokens:
        return [0.0] * len(documents)

    doc_lens = [len(doc) or 1 for doc in tokenized]
    avg_dl = sum(doc_lens) / len(doc_lens)
    df: Counter[str] = Counter()
    for doc in tokenized:
        df.update(set(doc))
    n = len(documents)

    scores: list[float] = []
    for doc, dl in zip(tokenized, doc_lens):
        tf = Counter(doc)
        score = 0.0
        for term in query_tokens:
            if term not in tf:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            freq = tf[term]
            denom = freq + k1 * (1 - b + b * dl / avg_dl)
            score += idf * (freq * (k1 + 1)) / denom
        scores.append(score)
    return scores


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (norm_a * norm_b)


def _normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return [0.5] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def hybrid_rank(
    chunks: list[TimelineChunk],
    query_embedding: list[float],
    query_text: str,
    limit: int = 6,
    vector_weight: float = 0.6,
) -> list[TimelineChunk]:
    if not chunks:
        return []

    documents = [
        " ".join(
            filter(
                None,
                [c.transcript_text, c.ocr_text, c.visual_summary, c.chapter_title or ""],
            )
        )
        for c in chunks
    ]

    vector_scores = [
        _cosine_similarity(query_embedding, chunk.embedding or []) if chunk.embedding else 0.0
        for chunk in chunks
    ]
    bm25_scores = _bm25_scores(query_text, documents)

    norm_v = _normalize(vector_scores)
    norm_b = _normalize(bm25_scores)

    combined = [
        (chunk, vector_weight * v + (1 - vector_weight) * b)
        for chunk, v, b in zip(chunks, norm_v, norm_b)
    ]
    combined.sort(key=lambda item: item[1], reverse=True)
    return [chunk for chunk, _ in combined[:limit]]
