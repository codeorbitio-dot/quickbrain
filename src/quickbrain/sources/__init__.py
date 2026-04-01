"""
Base interface for a search source.
All sources (Exa, Brave, Reddit, HN, GitHub Trending, Web Fetch) implement this.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class SearchResult:
    """A single result from any source."""
    title: str
    url: str
    snippet: str
    source: str          # name of the source (exa, brave, reddit, hn, github_trending, web_fetch)
    score: float = 0.0   # relevance/quality score (filled by scorer)
    published: str = ""   # ISO date or age string, if available
    metadata: dict = field(default_factory=dict)


class Source(ABC):
    """Pluggable search source."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def requires_config(self) -> bool:
        """Whether this source needs an API key or config."""

    @abstractmethod
    async def search(self, query: str, **kwargs) -> list[SearchResult]:
        ...

    def is_available(self) -> bool:
        """Return True if this source is configured and reachable."""
        return True


# Re-export concrete sources for convenience
from quickbrain.sources.exa_search import ExaSearch
from quickbrain.sources.brave_search import BraveSearch
from quickbrain.sources.hackernews import HackerNews
from quickbrain.sources.reddit import Reddit
from quickbrain.sources.github_trending import GitHubTrending
from quickbrain.sources.web_fetch import WebFetch

__all__ = [
    "SearchResult",
    "Source",
    "ExaSearch",
    "BraveSearch",
    "HackerNews",
    "Reddit",
    "GitHubTrending",
    "WebFetch",
]
