"""
Reddit — public JSON search, no API key needed.
"""

from __future__ import annotations

import httpx

from quickbrain.sources import Source, SearchResult


class Reddit(Source):
    """Reddit search via public JSON endpoint."""

    @property
    def name(self) -> str:
        return "reddit"

    def requires_config(self) -> bool:
        return False

    def is_available(self) -> bool:
        return True

    async def search(self, query: str, **kwargs) -> list[SearchResult]:
        num_results = kwargs.get("num_results", 10)
        url = f"https://www.reddit.com/search.json?q={query}&limit={num_results}&sort=relevance"
        headers = {"User-Agent": "QuickBrain/0.1.0"}

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for post in data.get("data", {}).get("children", []):
            d = post.get("data", {})
            url_val = d.get("url", "") or f"https://reddit.com{d.get('permalink', '')}"
            results.append(SearchResult(
                title=d.get("title", ""),
                url=url_val,
                snippet=(d.get("selftext", "")[:300] or d.get("title", "")),
                source="reddit",
                metadata={
                    "subreddit": d.get("subreddit", ""),
                    "score": d.get("score", 0),
                    "comments": d.get("num_comments", 0),
                    "author": d.get("author", ""),
                },
            ))
        return results
