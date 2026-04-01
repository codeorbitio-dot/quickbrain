"""Tests for CLI module."""
import pytest
import subprocess
import sys
import json


def test_cli_help():
    """CLI --help should not crash."""
    result = subprocess.run(
        [sys.executable, "-m", "quickbrain", "--help"],
        capture_output=True, text=True, timeout=10,
        cwd="/root/.openclaw/workspace/quickbrain",
    )
    assert result.returncode == 0 or "Usage" in result.stdout


def test_cli_no_args_exits():
    """CLI with no args should print usage and exit."""
    result = subprocess.run(
        [sys.executable, "-m", "quickbrain"],
        capture_output=True, text=True, timeout=10,
        cwd="/root/.openclaw/workspace/quickbrain",
    )
    output = result.stdout + result.stderr
    assert "Usage" in output or "quickbrain" in output.lower()


def test_cli_args_parsing(monkeypatch):
    """Test that argparse handles the new flags correctly."""
    from quickbrain.cli import build_parser
    parser = build_parser()

    # Normal search — argparse nargs="*" preserves spaces within each arg
    args = parser.parse_args(["my query"])
    assert args.query == ["my query"]
    # Two separate args
    args = parser.parse_args(["my", "query"])
    assert args.query == ["my", "query"]
    assert args.top == 7
    assert args.json_output is False
    assert args.watch == 0
    assert args.fetch is None

    # JSON + top
    args = parser.parse_args(["query", "--json", "--top", "3"])
    assert args.json_output is True
    assert args.top == 3

    # Watch
    args = parser.parse_args(["query", "--watch", "30"])
    assert args.watch == 30

    # Fetch
    args = parser.parse_args(["--fetch", "https://example.com"])
    assert args.fetch == "https://example.com"

    # Multiple flags
    args = parser.parse_args(["query", "--json", "--top", "5", "--watch", "60"])
    assert args.json_output is True
    assert args.top == 5
    assert args.watch == 60


def test_result_dict_structure():
    """Test SearchResult conversion to dict."""
    from quickbrain.sources import SearchResult
    from quickbrain.cli import _result_dict

    r = SearchResult(
        title="Test",
        url="https://example.com",
        snippet="A test result",
        source="test",
        score=0.85,
        published="2025-01-01",
        metadata={"key": "value"},
    )
    d = _result_dict(r)
    assert d["title"] == "Test"
    assert d["url"] == "https://example.com"
    assert d["snippet"] == "A test result"
    assert d["source"] == "test"
    assert d["score"] == 0.85
    assert d["published"] == "2025-01-01"
    assert d["metadata"] == {"key": "value"}


def test_result_dict_is_json_serializable():
    """Test that _result_dict output can be json.dumps'd."""
    from quickbrain.sources import SearchResult
    from quickbrain.cli import _result_dict

    r = SearchResult(
        title="Test",
        url="https://example.com",
        snippet="A test",
        source="hn",
        score=0.9,
        metadata={"nested": {"deep": True}},
    )
    d = _result_dict(r)
    # Should not raise
    json.dumps(d)


def test_results_signature_deterministic():
    """Same results should produce the same signature."""
    from quickbrain.sources import SearchResult
    from quickbrain.cli import _results_signature

    results = [
        SearchResult(title="A", url="https://a.dev", snippet="a", source="hn", score=0.9),
        SearchResult(title="B", url="https://b.dev", snippet="b", source="exa", score=0.8),
    ]
    sig1 = _results_signature(results, 2)
    sig2 = _results_signature(results, 2)
    assert sig1 == sig2


def test_results_signature_different():
    """Different results should produce different signatures."""
    from quickbrain.sources import SearchResult
    from quickbrain.cli import _results_signature

    results1 = [
        SearchResult(title="A", url="https://a.dev", snippet="a", source="hn", score=0.9),
    ]
    results2 = [
        SearchResult(title="B", url="https://b.dev", snippet="b", source="hn", score=0.9),
    ]
    assert _results_signature(results1, 1) != _results_signature(results2, 1)
