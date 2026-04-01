"""
Smart deduplication for search results.
Deduplicates by URL (exact match) and by content similarity (trigram/token Jaccard).
"""

from __future__ import annotations

import re
from quickbrain.sources import SearchResult


def _tokenize(text: str) -> set[str]:
    """Lowercase, extract alphanumeric tokens."""
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def _trigrams(text: str) -> set[str]:
    """Extract character trigrams from text."""
    t = text.lower()
    if len(t) < 3:
        return {t}
    return {t[i:i + 3] for i in range(len(t) - 2)}


def _jaccard(a: set, b: set) -> float:
    """Jaccard similarity between two sets."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _content_similarity(r1: SearchResult, r2: SearchResult) -> float:
    """Content similarity using token Jaccard and trigram Jaccard (max of both)."""
    text1 = f"{r1.title} {r1.snippet}"
    text2 = f"{r2.title} {r2.snippet}"
    token_sim = _jaccard(_tokenize(text1), _tokenize(text2))
    trigram_sim = _jaccard(_trigrams(text1), _trigrams(text2))
    return max(token_sim, trigram_sim)


def smart_dedup(results: list[SearchResult], threshold: float = 0.7) -> list[SearchResult]:
    """
    Smart deduplication:
    1. First pass — exact URL dedup (keep higher score).
    2. Second pass — content similarity dedup using token/trigram Jaccard.

    Args:
        results: list of SearchResult to deduplicate.
        threshold: Jaccard sim above which to deduplicate (default 0.7).

    Returns:
        Deduplicated list, keeping results with higher scores.
    """
    if len(results) <= 1:
        return list(results)

    # Sort by score descending — best ones come first
    results = sorted(results, key=lambda r: r.score, reverse=True)

    # Pass 1: URL dedup
    seen_urls: set[str] = set()
    url_unique: list[SearchResult] = []
    for r in results:
        if r.url not in seen_urls:
            seen_urls.add(r.url)
            url_unique.append(r)

    # Pass 2: content similarity dedup
    final: list[SearchResult] = []
    for r in url_unique:
        is_dup = False
        for existing in final:
            sim = _content_similarity(r, existing)
            if sim >= threshold:
                is_dup = True
                break
        if not is_dup:
            final.append(r)

    return final
