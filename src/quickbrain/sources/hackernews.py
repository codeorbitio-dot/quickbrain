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
            title = hit.get("title", "") or ""
            story_text = hit.get("story_text", "") or ""
            # Skip link-only posts with no title and no text
            if not title and not story_text:
                continue

            display_title = title or (story_text[:80] + "..." if len(story_text) > 80 else story_text[:80])
            story_url = hit.get("url", "") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            snippet = story_text[:300] if story_text else ""

            results.append(SearchResult(
                title=display_title,
                url=story_url,
                snippet=snippet,
                source="hackernews",
                published=hit.get("created_at", ""),
                metadata={
                    "points": hit.get("points", 0),
                    "comments": hit.get("num_comments", 0),
                    "author": hit.get("author", ""),
                },
            ))
        return results
