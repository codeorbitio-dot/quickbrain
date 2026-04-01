"""
Relevance scorer — scores search results against the original query.
"""

from __future__ import annotations

from quickbrain.sources import SearchResult


def score_relevance(results: list[SearchResult], query: str) -> list[SearchResult]:
    """Assign a relevance score (0.0 - 1.0) based on query overlap."""
    query_tokens = set(query.lower().split())

    for r in results:
        text = f"{r.title} {r.snippet}".lower()
        text_tokens = set(text.split())
        overlap = len(query_tokens & text_tokens) / max(len(query_tokens), 1)

        # Boost if title contains query terms
        title_tokens = set(r.title.lower().split())
        title_overlap = len(query_tokens & title_tokens) / max(len(query_tokens), 1)

        r.score = round(0.6 * overlap + 0.4 * title_overlap, 3)

    return sorted(results, key=lambda r: r.score, reverse=True)
