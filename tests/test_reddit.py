"""Tests for source interface and Reddit."""
import pytest

from quickbrain.sources import Source, SearchResult
from quickbrain.sources.hackernews import HackerNews
from quickbrain.sources.reddit import Reddit


def test_hn_interface():
    hn = HackerNews()
    assert hn.name == "hackernews"
    assert hn.requires_config() is False
    assert hn.is_available() is True


def test_reddit_interface():
    r = Reddit()
    assert r.name == "reddit"
    assert r.requires_config() is False
    assert r.is_available() is True


def test_search_result_defaults():
    sr = SearchResult(title="T", url="https://u.dev", snippet="S", source="test")
    assert sr.score == 0.0
    assert sr.published == ""
    assert sr.metadata == {}
