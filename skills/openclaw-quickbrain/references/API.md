# QuickBrain API Reference

## Overview
QuickBrain is a fast, lightweight web research agent that queries multiple sources in parallel, deduplicates, scores, and synthesizes results into a concise summary.

## Python API

### Search

```python
from quickbrain.search import search, get_sources

# Run a full multi-source search
results = await search("your query", num_results=10)

# Get list of configured sources
sources = get_sources()
```

Returns: `list[SearchResult]` sorted by relevance score.

### Individual Sources

```python
from quickbrain.sources import GitHubTrending, WebFetch

# GitHub Trending (no API key)
gt = GitHubTrending()
trending = await gt.search("python")

# Web Fetch (fetch specific URLs)
wf = WebFetch()
content = await wf.search("", urls=["https://example.com"])
```

### SearchResult

```python
from quickbrain.sources import SearchResult

result = SearchResult(
    title="Repo or article name",
    url="https://...",
    snippet="Short description",
    source="github_trending",  # which source found this
    score=0.85,                # relevance score (filled by scorer)
    metadata={"language": "Python", "stars_today": "1,234 stars today"},
)
```

### Smart Dedup

```python
from quickbrain.dedup import smart_dedup

deduped = smart_dedup(results, threshold=0.7)
```

## CLI

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON instead of Rich panel |
| `--top N` | Number of top results (default 7) |
| `--watch SEC` | Monitor query, re-check every N seconds |
| `--fetch URL` | Fetch content from a specific URL |

## Sources

| Source | API Key | Notes |
|--------|---------|-------|
| HackerNews | No | hn.algolia.com |
| Reddit | No | old.reddit.com |
| GitHub Trending | No | github.com/trending |
| Exa | Yes | EXA_API_KEY |
| Brave | Yes | BRAVE_API_KEY |
| Web Fetch | No | Fetch arbitrary URLs |
