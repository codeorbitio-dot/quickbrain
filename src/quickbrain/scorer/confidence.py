"""
Confidence scoring — composite score combining multiple signals.

Components (weights sum to 1.0):
  40%  semantic relevance  — from embedding scorer
  25%  freshness           — recency decay from metadata/created_at
  20%  cross-source        — convergence across distinct sources
  15%  source authority    — points/comments/upvotes metrics
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from quickbrain.sources import SearchResult


# ---------------------------------------------------------------------------
# Component scorers (each returns 0.0–1.0)
# ---------------------------------------------------------------------------


def _semantic_score(r: SearchResult) -> float:
    """Use the score already set by the embedding/relevance scorer."""
    return r.score


def _freshness_score(r: SearchResult) -> float:
    """Exponential decay: half-life 90 days. Missing date → neutral 0.5."""
    created = r.metadata.get("created_at") or r.published
    if not created:
        return 0.5  # neutral when unknown

    try:
        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400
        half_life = 90.0
        return math.exp(-math.log(2) * age_days / half_life)
    except (ValueError, TypeError):
        return 0.5


def _cross_source_score(results: list[SearchResult], r: SearchResult) -> float:
    """
    How well the query converges across distinct sources.

    More unique sources = higher confidence. Missing data or single source
    yields a moderate score.
    """
    sources_seen = set(res.source for res in results)
    if len(sources_seen) <= 1:
        return 0.4
    return min(len(sources_seen) / 3.0, 1.0)


def _authority_score(r: SearchResult) -> float:
    """
    Source authority from engagement metrics (points, comments, upvotes).
    Falls back to 0.5 (neutral) when no metadata is available.
    """
    metadata = r.metadata or {}
    points = int(metadata.get("points", 0))
    comments = int(metadata.get("comments", 0))
    upvotes = int(metadata.get("upvotes", 0))

    total = points + comments + upvotes
    if total == 0:
        return 0.5
    return min(total / 100.0, 1.0)


# ---------------------------------------------------------------------------
# Composite confidence
# ---------------------------------------------------------------------------

WEIGHTS = {
    "semantic": 0.40,
    "freshness": 0.25,
    "convergence": 0.20,
    "authority": 0.15,
}


def compute_confidence(
    result: SearchResult,
    results: list[SearchResult],
) -> dict[str, float]:
    """
    Compute a confidence breakdown for a single result.

    Returns a dict with keys matching WEIGHTS plus 'confidence' (composite).
    """
    components = {
        "semantic": _semantic_score(result),
        "freshness": _freshness_score(result),
        "convergence": _cross_source_score(results, result),
        "authority": _authority_score(result),
    }
    composite = sum(WEIGHTS[k] * v for k, v in components.items())
    components["confidence"] = round(composite, 3)
    return components


def score_with_confidence(
    query: str,
    results: list[SearchResult],
) -> list[SearchResult]:
    """
    Score results using semantic embedding, then compute composite confidence.

    Each result gets a ``confidence`` attribute (dict with component breakdown)
    and its ``score`` is updated to the composite confidence value.

    Returns results sorted by composite confidence descending.
    """
    from quickbrain.scorer.embedding import score_with_embedding

    scored = score_with_embedding(query, results)

    for r in scored:
        breakdown = compute_confidence(r, scored)
        setattr(r, "confidence", breakdown)
        r.score = breakdown["confidence"]

    return sorted(scored, key=lambda r: r.score, reverse=True)
