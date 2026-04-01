"""
Reddit — public JSON search, no API key needed.
Falls back to subreddit listings if the main search endpoint returns 403.
"""

from __future__ import annotations

import httpx
import re

from quickbrain.sources import Source, SearchResult


def _clean_html(text: str) -> str:
    """Remove HTML-ish entities like &#x27; from Reddit responses."""
    return re.sub(r"&#x[0-9a-fA-F]+;|&amp;", "", text).strip()


class Reddit(Source):
    """Reddit search via old.reddit.com endpoint."""

    @property
    def name(self) -> str:
        return "reddit"

    def requires_config(self) -> bool:
        return False

    def is_available(self) -> bool:
        return True

    async def _search_main(self, query: str, num_results: int) -> list[SearchResult]:
        url = f"https://old.reddit.com/search/.json?q={query}&limit={num_results}&sort=relevance"
        headers = {
            "User-Agent": "QuickBrain/0.1.0 (personal research tool)",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for post in data.get("data", {}).get("children", []):
            d = post.get("data", {})
            if d.get("over_18"):
                continue
            title = _clean_html(d.get("title", ""))
            selftext = _clean_html(d.get("selftext", ""))
            url_val = d.get("url", "") or f"https://reddit.com{d.get('permalink', '')}"

            # Skip low-quality posts - both title and text must not be empty
            if not title and not selftext:
                continue

            snippet = selftext[:300] if selftext else title[:300]
            results.append(SearchResult(
                title=title,
                url=url_val,
                snippet=snippet,
                source="reddit",
                metadata={
                    "subreddit": d.get("subreddit", ""),
                    "score": d.get("score", 0),
                    "comments": d.get("num_comments", 0),
                    "author": d.get("author", ""),
                },
            ))
        return results

    async def _search_fallback(self, query: str, num_results: int) -> list[SearchResult]:
        """Fallback: search in popular tech subreddits via /hot."""
        subreddits = ["programming", "MachineLearning", "artificial", "LocalLLaMA", "datascience"]
        results = []
        headers = {"User-Agent": "QuickBrain/0.1.0 (personal research tool)"}

        async with httpx.AsyncClient(follow_redirects=True) as client:
            for sub in subreddits[:3]:
                try:
                    url = f"https://old.reddit.com/r/{sub}/hot/.json?limit=25"
                    resp = await client.get(url, headers=headers, timeout=10)
                    if resp.status_code != 200:
                        continue
                    data = resp.json()
                    for post in data.get("data", {}).get("children", []):
                        d = post.get("data", {})
                        title = _clean_html(d.get("title", ""))
                        if d.get("over_18") or not title:
                            continue
                        # Simple text match — check if query terms appear in title/text
                        query_lower = query.lower()
                        text_lower = (title + " " + d.get("selftext", "")[:200]).lower()
                        if any(term in text_lower for term in query_lower.split()):
                            results.append(SearchResult(
                                title=title,
                                url=d.get("url", "") or f"https://reddit.com{d.get('permalink', '')}",
                                snippet=_clean_html(d.get("selftext", ""))[:300] or title,
                                source="reddit",
                                metadata={
                                    "subreddit": d.get("subreddit", ""),
                                    "score": d.get("score", 0),
                                    "comments": d.get("num_comments", 0),
                                    "author": d.get("author", ""),
                                },
                            ))
                            if len(results) >= num_results:
                                return results
                except Exception:
                    continue
        return results[:num_results]

    async def search(self, query: str, **kwargs) -> list[SearchResult]:
        num_results = kwargs.get("num_results", 10)

        try:
            return await self._search_main(query, num_results)
        except Exception:
            try:
                return await self._search_fallback(query, num_results)
            except Exception:
                return []
