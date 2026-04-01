"""
Search orchestrator — runs multiple sources in parallel, dedupes, scores.
"""

from __future__ import annotations

import asyncio
from quickbrain.sources import Source, SearchResult
from quickbrain.sources.exa_search import ExaSearch
from quickbrain.sources.brave_search import BraveSearch
from quickbrain.sources.hackernews import HackerNews
from quickbrain.sources.reddit import Reddit
from quickbrain.scorer.relevance import score_relevance


def get_sources() -> list[Source]:
    """Build list of available sources based on config."""
    sources: list[Source] = []

    # Always available (free, no API key)
    sources.append(HackerNews())
    sources.append(Reddit())

    # Exa — most impactful source, add if configured
    exa = ExaSearch()
    if exa.is_available():
        sources.append(exa)

    # Brave — secondary web search
    brave = BraveSearch()
    if brave.is_available():
        sources.append(brave)

    return sources


async def search(query: str, num_results: int = 10) -> list[SearchResult]:
    """
    Run parallel search across all available sources, combine, score, return.
    """
    sources = get_sources()
    if not sources:
        raise RuntimeError("No search sources configured. Set EXA_API_KEY or BRAVE_API_KEY.")

    # Run all sources in parallel
    tasks = [s.search(query, num_results=num_results) for s in sources]
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Flatten + filter errors
    results: list[SearchResult] = []
    for raw in raw_results:
        if isinstance(raw, Exception):
            continue  # skip failed sources, don't fail the whole search
        results.extend(raw)

    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for r in results:
        if r.url not in seen_urls:
            seen_urls.add(r.url)
            unique.append(r)

    # Score and sort
    return score_relevance(unique, query)
