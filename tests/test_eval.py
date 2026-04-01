"""Tests for the eval harness — scoring metrics and benchmark."""
import pytest
from quickbrain.sources import SearchResult
from quickbrain.eval import (
    precision_at_k,
    ndcg_at_k,
    _terms_match,
    GOLDEN_QUERIES,
)


def test_terms_match_basic():
    assert _terms_match("machine learning deep", ["learning"]) is True


def test_terms_match_case_insensitive():
    assert _terms_match("Machine Learning", ["machine"]) is True


def test_terms_match_no_hit():
    assert _terms_match("cooking recipe", ["neural", "ai"]) is False


def test_terms_match_substring():
    """Substrings should match, not just word boundaries."""
    assert _terms_match("benchmarking", ["bench"]) is True


def test_precision_at_k_all_hits():
    results = [
        SearchResult(title="ML intro", url="https://a.dev", snippet="machine learning", source="hn"),
        SearchResult(title="neural networks", url="https://b.dev", snippet="deep learning model", source="exa"),
        SearchResult(title="AI tutorial", url="https://c.dev", snippet="artificial intelligence", source="reddit"),
    ]
    assert precision_at_k(results, ["learning", "ai"], 3) == 1.0


def test_precision_at_k_no_hits():
    results = [
        SearchResult(title="cooking", url="https://a.dev", snippet="recipe", source="hn"),
    ]
    assert precision_at_k(results, ["quantum", "physics"], 1) == 0.0


def test_precision_at_k_empty_results():
    assert precision_at_k([], ["test"], 3) == 0.0


def test_ndcg_at_k_ideal():
    """All relevant — NDCG should be 1.0."""
    results = [
        SearchResult(title="neural learning", url="https://a.dev", snippet="deep neural network", source="hn"),
        SearchResult(title="machine learning", url="https://b.dev", snippet="ML model training", source="exa"),
    ]
    assert ndcg_at_k(results, ["learning", "neural"], 2) == pytest.approx(1.0)


def test_golden_queries_count():
    """Should have at least 20 golden queries for evals."""
    assert len(GOLDEN_QUERIES) >= 20
