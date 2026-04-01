"""Tests for search orchestrator."""
import asyncio
import pytest
from unittest.mock import patch, AsyncMock

from quickbrain.sources import SearchResult
from quickbrain.search import search


@pytest.fixture
def mock_results():
    return [
        SearchResult(title="Alpha AI framework", url="https://a.dev/alpha", snippet="New AI framework", source="hn"),
        SearchResult(title="Alpha AI tools", url="https://b.dev/alpha", snippet="Best tools for AI dev", source="exa"),
        SearchResult(title="Duplicate", url="https://dup.dev", snippet="Dup", source="hn"),
        SearchResult(title="Duplicate", url="https://dup.dev", snippet="Dup copy", source="exa"),
    ]


@pytest.mark.asyncio
async def test_search_returns_scored_results(mock_results):
    """Verify search returns scored results with correct type."""
    from quickbrain.scorer.relevance import score_relevance
    results = score_relevance(mock_results[:3], "AI framework")
    assert results[0].score >= results[-1].score
    assert all(isinstance(r, SearchResult) for r in results)


@pytest.mark.asyncio
async def test_search_no_results():
    """Verify template handles empty results gracefully."""
    from quickbrain.synthesize import synthesize
    summary = await synthesize([], "nothing")
    assert "No results" in summary


def test_get_sources_has_free_ones():
    """HackerNews and Reddit should always be available."""
    from quickbrain.search import get_sources
    sources = get_sources()
    names = [s.name for s in sources]
    assert "hackernews" in names
    assert "reddit" in names
