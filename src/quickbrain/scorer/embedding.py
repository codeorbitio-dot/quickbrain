"""
Semantic scoring using sentence-transformers embeddings.
Falls back to keyword overlap if the library is unavailable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from quickbrain.sources import SearchResult
from quickbrain.scorer.relevance import score_relevance as _fallback_score

if TYPE_CHECKING:
    pass

_MODULE_AVAILABLE: bool | None = None


def _sentence_transformers_available() -> bool:
    """Check if sentence-transformers can be imported (cached result)."""
    global _MODULE_AVAILABLE
    if _MODULE_AVAILABLE is None:
        try:
            import sentence_transformers  # noqa: F401
            _MODULE_AVAILABLE = True
        except ImportError:
            _MODULE_AVAILABLE = False
    return _MODULE_AVAILABLE


_embedding_model = None


def _get_model():
    """Cache the model at module level — don't reload on every call."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def cosine_sim(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two 1-D vectors (no sklearn needed)."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def score_with_embedding(
    query: str,
    results: list[SearchResult],
) -> list[SearchResult]:
    """
    Score search results using semantic embeddings.

    Embeds the query via sentence-transformers, computes cosine similarity
    with each result's (title + snippet) text, and sorts descending.

    Falls back to keyword overlap scoring if sentence-transformers is not installed.

    Returns:
        Results sorted by semantic relevance score (0.0–1.0).
    """
    if not _sentence_transformers_available():
        return _fallback_score(results, query)

    if not results:
        return results

    model = _get_model()
    query_emb = model.encode(query, convert_to_numpy=True).tolist()

    for r in results:
        text = f"{r.title}. {r.snippet}"
        result_emb = model.encode(text, convert_to_numpy=True).tolist()
        sim = cosine_sim(query_emb, result_emb)
        # Cosine similarity ranges [-1, 1]; map to [0, 1]
        r.score = round((sim + 1) / 2, 3)

    return sorted(results, key=lambda r: r.score, reverse=True)
