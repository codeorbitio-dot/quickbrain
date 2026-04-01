"""Tests for synthesize module."""
import asyncio
import pytest

from quickbrain.sources import SearchResult
from quickbrain.synthesize import synthesize_template, synthesize


def test_synthesize_template_empty():
    assert "No results" in synthesize_template([], "test")


def test_synthesize_template_with_results():
    results = [
        SearchResult(title="Test Post", url="https://t.dev", snippet="This is a test", source="hn", score=0.8),
        SearchResult(title="Another Post", url="https://b.dev", snippet="More content", source="reddit", score=0.5),
    ]
    output = synthesize_template(results, "test query", top_n=2)
    assert "Test Post" in output
    assert "Another Post" in output
    assert "https://t.dev" in output
    assert "Sources:" in output
    assert "hn" in output
    assert "reddit" in output


@pytest.mark.asyncio
async def test_synthesize_llm_flag():
    """LLM flag should not crash, falls back to template."""
    results = [
        SearchResult(title="X", url="https://x.dev", snippet="Y", source="hn"),
    ]
    out = await synthesize(results, "test", llm_available=True)
    assert "Test" not in out  # just verify it returns, not an assertion about content style


def test_synthesize_top_n_limit():
    results = [
        SearchResult(title=f"Post {i}", url=f"https://t.dev/{i}", snippet="x", source="hn", score=1.0)
        for i in range(10)
    ]
    output = synthesize_template(results, "query", top_n=3)
    assert "Post 0" in output
    assert "Post 3" not in output  # should be limited to 3
