"""
Web Fetch — fetch readable content from specific URLs.
Uses httpx to fetch URLs and strips HTML tags for clean text extraction.
"""

from __future__ import annotations

import re
import httpx

from quickbrain.sources import Source, SearchResult


# Compiled regex for common HTML stripping
_SCRIPT_STYLE_RE = re.compile(r'<(script|style)[^>]*>.*?</\1>', re.DOTALL | re.IGNORECASE)
_HTML_TAG_RE = re.compile(r'<[^>]+>')
_COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)
_WHITESPACE_RE = re.compile(r'\s+')


def _strip_html(html: str) -> str:
    """Remove HTML tags and return clean text."""
    # Remove script/style content
    text = _SCRIPT_STYLE_RE.sub('', html)
    # Remove comments
    text = _COMMENT_RE.sub('', text)
    # Remove all other tags
    text = _HTML_TAG_RE.sub(' ', text)
    # Decode common HTML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    # Collapse whitespace
    text = _WHITESPACE_RE.sub(' ', text).strip()
    return text


_TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)


class WebFetch(Source):
    """Fetch and extract readable content from specific URLs.

    Unlike other sources, this doesn't 'search' — it fetches content
    directly from user-provided URLs.

    Usage:
        source = WebFetch()
        results = await source.search("ignored_query", urls=["https://example.com"])
    """

    @property
    def name(self) -> str:
        return "web_fetch"

    def requires_config(self) -> bool:
        return False

    def is_available(self) -> bool:
        return True

    async def search(self, query: str, **kwargs) -> list[SearchResult]:
        """Fetch content from URLs provided via kwargs['urls'].

        Args:
            query: Ignored (kept for interface compatibility).
            urls: A single URL string or list of URL strings to fetch.

        Returns:
            List[SearchResult] with extracted text as snippet.
        """
        urls = kwargs.get("urls", [])
        if isinstance(urls, str):
            urls = [urls]

        if not urls:
            return []

        results: list[SearchResult] = []
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            for url in urls:
                try:
                    resp = await client.get(
                        url,
                        headers={"User-Agent": "QuickBrain/0.1.0 (personal research tool)"},
                    )
                    resp.raise_for_status()

                    content_type = resp.headers.get("Content-Type", "")
                    html = resp.text
                    text = _strip_html(html)

                    # Try to extract page title
                    title_match = _TITLE_RE.search(html)
                    title = title_match.group(1).strip() if title_match else url

                    # Snippet is first 500 chars of cleaned text
                    snippet = text[:500] if text else "(empty page)"

                    results.append(SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source="web_fetch",
                        metadata={
                            "content_length": len(text),
                            "status_code": resp.status_code,
                        },
                    ))
                except Exception as e:
                    results.append(SearchResult(
                        title=f"Failed to fetch: {url}",
                        url=url,
                        snippet=f"Error: {e}",
                        source="web_fetch",
                        metadata={"error": str(e)},
                    ))

        return results
