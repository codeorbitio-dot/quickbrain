"""
Exa AI — semantic search, the most impactful source for QuickBrain.
Free tier: 1000 searches/month.
"""

from __future__ import annotations

import os
from exa_py import Exa

from quickbrain.sources import Source, SearchResult


class ExaSearch(Source):
    """Exa AI semantic web search."""

    @property
    def name(self) -> str:
        return "exa"

    def requires_config(self) -> bool:
        return True

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("EXA_API_KEY")
        self._client: Exa | None = None

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def search(self, query: str, **kwargs) -> list[SearchResult]:
        if not self._client:
            self._client = Exa(api_key=self._api_key)

        num_results = kwargs.get("num_results", 10)

        results = self._client.search_and_contents(
            query,
            num_results=num_results,
            text=True,
        )

        return [
            SearchResult(
                title=r.title or "Untitled",
                url=r.url,
                snippet=(r.text[:500] if r.text else ""),
                source="exa",
                published="",
            )
            for r in results.results
        ]
