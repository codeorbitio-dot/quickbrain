"""
Brave Search — web search fallback/secondary source.
Free tier: 2000 queries/month.
"""

from __future__ import annotations

import os
import httpx

from quickbrain.sources import Source, SearchResult


class BraveSearch(Source):
    """Brave web search."""

    @property
    def name(self) -> str:
        return "brave"

    def requires_config(self) -> bool:
        return True

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("BRAVE_API_KEY")
        self._base = "https://api.search.brave.com/res/v1/web/search"

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def search(self, query: str, **kwargs) -> list[SearchResult]:
        if not self.is_available():
            return []

        headers = {"Accept": "application/json", "X-Subscription-Token": self._api_key}
        num_results = kwargs.get("num_results", 10)

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self._base,
                params={"q": query, "count": num_results},
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for r in data.get("web", {}).get("results", []):
            results.append(SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("description", ""),
                source="brave",
            ))
        return results
