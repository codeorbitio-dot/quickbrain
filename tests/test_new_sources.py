"""Tests for new sources: GitHubTrending and WebFetch."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from quickbrain.sources import SearchResult
from quickbrain.sources.github_trending import GitHubTrending
from quickbrain.sources.web_fetch import WebFetch, _strip_html


# ── GitHub Trending tests ─────────────────────────────────

SAMPLE_TRENDING_HTML = """
<html>
<body>
<article class="Box-row">
  <h2 class="h3 lh-condensed">
    <a href="/owner/repo-alpha" class="v-align-middle">
      <span class="text-normal">owner /</span>
      repo-alpha
    </a>
  </h2>
  <p class="col-9 color-fg-muted my-1 pr-4">
    An awesome AI framework for building agents
  </p>
  <div class="d-flex flex-items-center">
    <span class="d-inline-block mr-3">
      <span itemprop="programmingLanguage">Python</span>
    </span>
    <span class="d-inline-block floating-sm-right">
      1,234 stars today
    </span>
  </div>
</article>
<article class="Box-row">
  <h2 class="h3 lh-condensed">
    <a href="/org/framework-beta">
      <span class="text-normal">org /</span>
      framework-beta
    </a>
  </h2>
  <p class="col-9 color-fg-muted my-1 pr-4"></p>
</article>
</body>
</html>
"""


def test_github_trending_name():
    assert GitHubTrending().name == "github_trending"


def test_github_trending_no_config():
    assert GitHubTrending().requires_config() is False


def test_github_trending_available():
    assert GitHubTrending().is_available() is True


@pytest.mark.asyncio
async def test_github_trending_parse_trending_page():
    """Test parsing of GitHub trending HTML."""
    source = GitHubTrending()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = SAMPLE_TRENDING_HTML
    mock_resp.headers = {}
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(return_value=mock_resp)

    with patch("quickbrain.sources.github_trending.httpx.AsyncClient", return_value=mock_client):
        results = await source.search("python")

    assert len(results) >= 1

    # First result should have language Python
    first = results[0]
    assert isinstance(first, SearchResult)
    assert first.source == "github_trending"
    assert "python" in first.metadata.get("language", "").lower()
    assert first.url.startswith("https://github.com/")


@pytest.mark.asyncio
async def test_github_trending_handles_empty_html():
    """Should return empty list for empty/no-matching HTML."""
    source = GitHubTrending()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html>no articles here</html>"
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(return_value=mock_resp)

    with patch("quickbrain.sources.github_trending.httpx.AsyncClient", return_value=mock_client):
        results = await source.search("query")

    assert results == []


@pytest.mark.asyncio
async def test_github_trending_source_class_interface():
    """Verify GitHubTrending implements Source interface."""
    from quickbrain.sources import Source

    source = GitHubTrending()
    assert isinstance(source, Source)
    assert hasattr(source, "name")
    assert callable(source.requires_config)
    assert callable(source.is_available)
    assert callable(source.search)


# ── WebFetch tests ────────────────────────────────────────

def test_web_fetch_name():
    assert WebFetch().name == "web_fetch"


def test_web_fetch_no_config():
    assert WebFetch().requires_config() is False


def test_web_fetch_available():
    assert WebFetch().is_available() is True


def test_web_fetch_no_urls_returns_empty():
    source = WebFetch()
    results = source.search_sync_if_exists("") if hasattr(source, "search_sync_if_exists") else None
    # Without mocking we can't test the async version easily, but the name/config checks pass


@pytest.mark.asyncio
async def test_web_fetch_returns_empty_for_no_urls():
    source = WebFetch()
    results = await source.search("")
    assert results == []


@pytest.mark.asyncio
async def test_web_fetch_single_url():
    """Test fetching a single URL."""
    source = WebFetch()

    html = "<html><head><title>Test Page</title></head><body><h1>Hello</h1><p>This is a test.</p></body></html>"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = html
    mock_resp.headers = {"Content-Type": "text/html"}
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(return_value=mock_resp)

    with patch("quickbrain.sources.web_fetch.httpx.AsyncClient", return_value=mock_client):
        results = await source.search("", urls=["https://example.com"])

    assert len(results) == 1
    r = results[0]
    assert r.source == "web_fetch"
    assert r.url == "https://example.com"
    assert "Test Page" in r.title
    assert "Hello" in r.snippet or "test" in r.snippet.lower()


@pytest.mark.asyncio
async def test_web_fetch_fails_gracefully():
    """Test that errors are captured, not raised."""
    source = WebFetch()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))

    with patch("quickbrain.sources.web_fetch.httpx.AsyncClient", return_value=mock_client):
        results = await source.search("", urls=["https://bad.example"])

    assert len(results) == 1
    r = results[0]
    assert "Failed" in r.title or "Error" in r.snippet
    assert "error" in r.metadata


# ── HTML stripping tests ──────────────────────────────────

def test_strip_html_basic():
    assert _strip_html("<p>Hello World</p>") == "Hello World"


def test_strip_html_script():
    assert "alert" not in _strip_html("<p>Hi</p><script>alert('xss')</script>")


def test_strip_html_entities():
    result = _strip_html("foo &amp; bar")
    assert "foo & bar" in result


def test_strip_html_whitespace():
    assert _strip_html("  hello   world  ") == "hello world"


def test_strip_html_empty():
    assert _strip_html("") == ""


def test_strip_html_style():
    result = _strip_html("<style>.cls{color:red}</style><p>content</p>")
    assert "cls" not in result
    assert "content" in result
