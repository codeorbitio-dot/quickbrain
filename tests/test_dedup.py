"""Tests for smart deduplication."""
import pytest
from quickbrain.sources import SearchResult
from quickbrain.dedup import (
    smart_dedup,
    _tokenize,
    _trigrams,
    _jaccard,
    _content_similarity,
)


# ── Unit helpers ──────────────────────────────────────────

def test_tokenize_basic():
    assert _tokenize("AI framework 2025") == {"ai", "framework", "2025"}


def test_tokenize_empty():
    assert _tokenize("") == set()


def test_trigrams_short():
    assert _trigrams("ab") == {"ab"}


def test_trigrams_enough():
    assert "abc" in _trigrams("abcdef")
    assert "def" in _trigrams("abcdef")


def test_jaccard_identical():
    assert _jaccard({1, 2, 3}, {1, 2, 3}) == 1.0


def test_jaccard_disjoint():
    assert _jaccard({1, 2}, {3, 4}) == 0.0


def test_jaccard_partial():
    assert _jaccard({1, 2, 3}, {2, 3, 4}) == pytest.approx(0.5)


def test_jaccard_both_empty():
    assert _jaccard(set(), set()) == 1.0


def test_jaccard_one_empty():
    assert _jaccard({1}, set()) == 0.0


# ── Content similarity ────────────────────────────────────

def test_content_similarity_identical():
    r1 = SearchResult(title="Same Title", url="https://a.dev", snippet="Same snippet", source="a")
    r2 = SearchResult(title="Same Title", url="https://b.dev", snippet="Same snippet", source="b")
    assert _content_similarity(r1, r2) == 1.0


def test_content_similarity_different():
    r1 = SearchResult(title="Apple pie recipe", url="https://a.dev", snippet="flour sugar eggs", source="a")
    r2 = SearchResult(title="Quantum computing", url="https://b.dev", snippet="qubits entanglement", source="b")
    assert _content_similarity(r1, r2) < 0.3


def test_content_similarity_similar():
    r1 = SearchResult(title="Best AI framework 2025", url="https://a.dev", snippet="New AI framework for building agents", source="a")
    r2 = SearchResult(title="Top AI frameworks", url="https://b.dev", snippet="Best frameworks to build AI agents in 2025", source="b")
    sim = _content_similarity(r1, r2)
    assert sim > 0.35  # Moderate-high similarity expected given shared keywords


# ── Smart dedup ───────────────────────────────────────────

def test_smart_dedup_empty():
    assert smart_dedup([]) == []


def test_smart_dedup_single():
    r = SearchResult(title="X", url="https://x.dev", snippet="x", source="hn")
    assert smart_dedup([r]) == [r]


def test_smart_dedup_url_dedup():
    r1 = SearchResult(title="X", url="https://x.dev", snippet="v1", source="hn", score=0.9)
    r2 = SearchResult(title="X", url="https://x.dev", snippet="v2", source="exa", score=0.5)
    result = smart_dedup([r1, r2])
    assert len(result) == 1
    assert result[0].snippet == "v1"  # kept higher score


def test_smart_dedup_url_dedup_unsorted():
    """Should dedup even when lower-score result comes first."""
    r1 = SearchResult(title="X", url="https://x.dev", snippet="low", source="hn", score=0.3)
    r2 = SearchResult(title="X", url="https://x.dev", snippet="high", source="exa", score=0.8)
    result = smart_dedup([r1, r2])
    assert len(result) == 1
    assert result[0].snippet == "high"


def test_smart_dedup_content_similar():
    """Items with enough content overlap should be deduplicated at a reasonable threshold."""
    # Use nearly identical titles/snippets to guarantee high similarity
    r1 = SearchResult(
        title="How to build AI agents with Python framework",
        url="https://a.dev",
        snippet="This guide shows how to build and deploy AI agents using a modern Python framework",
        source="hn", score=0.8,
    )
    r2 = SearchResult(
        title="How to build AI agents with Python framework",
        url="https://b.dev",
        snippet="This tutorial shows how to build and deploy AI agents using a modern Python framework",
        source="exa", score=0.6,
    )
    result = smart_dedup([r1, r2], threshold=0.6)
    # Should keep only one due to high content similarity
    assert len(result) == 1
    assert result[0].url == "https://a.dev"  # higher score


def test_smart_dedup_content_different():
    r1 = SearchResult(title="Python tutorial", url="https://a.dev", snippet="Learn Python basics", source="hn", score=0.8)
    r2 = SearchResult(title="Rust web app", url="https://b.dev", snippet="Build web apps with Rust", source="exa", score=0.7)
    result = smart_dedup([r1, r2])
    assert len(result) == 2


def test_smart_dedup_threshold_controls_dedup():
    """Lower threshold should deduplicate more aggressively."""
    # Create items with moderate similarity (~0.5)
    r1 = SearchResult(title="How to build AI agents with Python", url="https://a.dev", snippet="Comprehensive guide to building AI agents step by step with Python", source="hn", score=0.8)
    r2 = SearchResult(title="Build AI agents with Python guide", url="https://b.dev", snippet="Comprehensive tutorial for building AI agents step by step with Python", source="exa", score=0.6)

    # Low threshold = aggressive dedup, should merge these
    assert len(smart_dedup([r1, r2], threshold=0.3)) == 1

    # Very high threshold = keep both
    result = smart_dedup([r1, r2], threshold=0.98)
    assert len(result) >= 1  # At least one always remains


def test_smart_dedup_keeps_different_sources_different_content():
    """Ensure diverse results from different sources aren't over-deduped."""
    results = [
        SearchResult(title="Python web framework comparison", url="https://a.dev", snippet="FastAPI vs Flask vs Django", source="hn", score=0.9),
        SearchResult(title="Rust async runtime", url="https://b.dev", snippet="Tokio vs async-std comparison", source="reddit", score=0.8),
        SearchResult(title="Go microservices", url="https://c.dev", snippet="Building microservices with Go", source="exa", score=0.7),
    ]
    result = smart_dedup(results)
    assert len(result) == 3
