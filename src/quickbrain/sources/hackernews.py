"""
Hacker News — free, no API key needed.
"""

from __future__ import annotations

import httpx

from quickbrain.sources import Source, SearchResult


class HackerNews(Source):
    """Hacker News stories (free, no API key needed)."""

    @property
    def name(self) -> str:
        return "hackernews"

    def requires_config(self) -> bool:
        return False

    def is_available(self) -> bool:
        return True

    async def search(self, query: str, **kwargs) -> list[SearchResult]:
        num_results = kwargs.get("num_results", 10)
        url = f"https://hn.algolia.com/api/v1/search?query={query}&hitsPerPage={num_results}"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for hit in data.get("hits", []):
            story_url = hit.get("url", "") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            results.append(SearchResult(
                title=hit.get("title", ""),
                url=story_url,
                snippet=hit.get("story_text", "")[:300] or "",
                source="hackernews",
                published=hit.get("created_at", ""),
                metadata={
                    "points": hit.get("points", 0),
                    "comments": hit.get("num_comments", 0),
                    "author": hit.get("author", ""),
                },
            ))
        return results
