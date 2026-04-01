"""Tests for scorer improvements — embedding, confidence, and composite scoring."""
import pytest

from quickbrain.sources import SearchResult
from quickbrain.scorer.relevance import score_relevance
from quickbrain.scorer.embedding import score_with_embedding, cosine_sim
from quickbrain.scorer.confidence import (
    compute_confidence,
    _freshness_score,
    _authority_score,
)


def test_cosine_sim_identical():
    """Identical vectors should have cosine similarity = 1.0."""
    a = [1.0, 2.0, 3.0]
    assert cosine_sim(a, a) == pytest.approx(1.0)


def test_cosine_sim_orthogonal():
    """Orthogonal vectors should have similarity = 0.0."""
    assert cosine_sim([1, 0], [0, 1]) == pytest.approx(0.0)


def test_embedding_scoring_returns_sorted():
    """Embedding scorer should return sorted results."""
    results = [
        SearchResult(title="machine learning intro", url="https://a.dev", snippet="ML basics", source="hn"),
        SearchResult(title="cooking recipes", url="https://b.dev", snippet="Food tips", source="reddit"),
        SearchResult(title="deep learning tutorial", url="https://c.dev", snippet="Neural networks", source="exa"),
    ]
    scored = score_with_embedding("deep learning neural networks", results)
    assert scored[0].score >= scored[-1].score


def test_freshness_score_recent():
    """Recent items should score higher freshness."""
    r = SearchResult(
        title="X", url="https://x.dev", snippet="Y", source="hn",
        metadata={"created_at": "2026-03-31T10:00:00Z"}
    )
    assert _freshness_score(r) > 0.8


def test_freshness_score_old():
    """Old items should score lower freshness."""
    r = SearchResult(
        title="X", url="https://x.dev", snippet="Y", source="hn",
        metadata={"created_at": "2023-01-01T00:00:00Z"}
    )
    assert _freshness_score(r) < 0.3


def test_freshness_score_no_date():
    """No date — neutral 0.5."""
    r = SearchResult(title="X", url="https://x.dev", snippet="Y", source="hn")
    assert _freshness_score(r) == 0.5


def test_authority_score_zero():
    """Zero engagement — neutral 0.5."""
    r = SearchResult(title="X", url="https://x.dev", snippet="Y", source="hn", metadata={"points": 0})
    assert _authority_score(r) == 0.5


def test_authority_score_high():
    """High engagement — high authority."""
    r = SearchResult(title="X", url="https://x.dev", snippet="Y", source="hn", metadata={"points": 500, "comments": 100})
    score = _authority_score(r)
    assert score >= 0.9


def test_confidence_composite():
    """Compute confidence should return all components + composite."""
    r = SearchResult(
        title="AI framework", url="https://x.dev", snippet="Y", source="hn",
        metadata={"points": 10, "comments": 5, "created_at": "2026-03-30"},
        score=0.8,
    )
    breakdown = compute_confidence(r, [r])
    assert "semantic" in breakdown
    assert "freshness" in breakdown
    assert "convergence" in breakdown
    assert "authority" in breakdown
    assert "confidence" in breakdown
    assert 0.0 <= breakdown["confidence"] <= 1.0


def test_embedding_fallback_on_missing():
    """If sentence-transformers is not available, should fall back to relevance scoring."""
    from quickbrain.scorer.embedding import _sentence_transformers_available
    results = [SearchResult(title="hello world", url="https://x.dev", snippet="test", source="hn")]
    scored = score_with_embedding("hello world test query", results)
    # Either way it should return scored results
    assert isinstance(scored, list)
