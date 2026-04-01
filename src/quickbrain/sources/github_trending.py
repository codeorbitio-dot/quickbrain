"""
GitHub Trending — scrape trending repos page, no API key needed.
"""

from __future__ import annotations

import re

import httpx

from quickbrain.sources import Source, SearchResult

_ARTICLE_RE = re.compile(r'<article\s+class="Box-row">(.*?)</article>', re.DOTALL)
_HREF_RE = re.compile(r'<a\s+href="(/[^"]+)"')
_DESC_RE = re.compile(r'<p[^>]*>(.*?)</p>', re.DOTALL)
_LANG_RE = re.compile(r'<span\s+itemprop="programmingLanguage">([^<]+)</span>')
_STARS_RE = re.compile(r'([\d,]+)\s+stars?\s+(today|this\s+week)')


class GitHubTrending(Source):
    """Scrape https://github.com/trending."""

    @property
    def name(self) -> str:
        return "github_trending"

    def requires_config(self) -> bool:
        return False

    def is_available(self) -> bool:
        return True

    async def search(self, query: str, **kwargs) -> list[SearchResult]:
        url = "https://github.com/trending"
        headers = {"User-Agent": "QuickBrain/0.1.0"}

        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            html = resp.text

        limit = kwargs.get("num_results", 10)
        results: list[SearchResult] = []

        for article in _ARTICLE_RE.findall(html):
            href_match = _HREF_RE.search(article)
            if not href_match:
                continue

            repo_path = href_match.group(1).strip("/")
            repo_url = f"https://github.com/{repo_path}"
            title = repo_path

            desc_match = _DESC_RE.search(article)
            desc_text = re.sub(r'<[^>]+>', ' ', desc_match.group(1)).strip() if desc_match else ""

            lang_m = _LANG_RE.search(article)
            language = lang_m.group(1).strip() if lang_m else ""

            stars_m = _STARS_RE.search(article)
            stars_today = stars_m.group(0).strip() if stars_m else ""

            if query:
                q = query.lower()
                if q not in title.lower() and q not in language.lower() and q not in desc_text.lower():
                    continue

            results.append(SearchResult(
                title=title,
                url=repo_url,
                snippet=desc_text,
                source="github_trending",
                metadata={"language": language, "stars_today": stars_today},
            ))

            if len(results) >= limit:
                break

        return results
