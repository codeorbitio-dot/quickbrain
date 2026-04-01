---
name: quickbrain
description: Fast web research agent. Search Reddit, HN, Exa, GitHub Trending for query-based research. Use when user asks to search the web, find info, research a topic, look up what's trending, or get quick summaries.
---

# QuickBrain Skill

Fast, lightweight research agent that queries multiple sources in parallel, deduplicates, scores, and synthesizes results.

## Quick Start

```bash
# Basic search
python -m quickbrain "AI agent frameworks 2025"

# JSON output for programmatic use
python -m quickbrain "Rust web frameworks" --json --top 5

# Monitor a query for changes
python -m quickbrain "OpenClaw" --watch 60

# Fetch content from a URL
python -m quickbrain --fetch "https://github.com/features/actions"
```

## Sources

| Source | API Key | Description |
|--------|---------|-------------|
| HackerNews | No | Stories via hn.algolia.com |
| Reddit | No | Posts via old.reddit.com |
| GitHub Trending | No | Trending repos from GitHub |
| Exa | Yes (`EXA_API_KEY`) | AI-powered web search |
| Brave | Yes (`BRAVE_API_KEY`) | Brave Search API |
| Web Fetch | No | Fetch and extract content from URLs |

## CLI Flags

| Flag | Description |
|------|-------------|
| `--json` | Output structured JSON instead of Rich panels |
| `--top N` | Number of results to show (default 7) |
| `--watch SECONDS` | Monitor query, re-check every N seconds |
| `--fetch URL` | Fetch content from specific URL(s) |
| `--help` | Show help message |

## Output Format

Results are sorted by relevance score. Each result includes:

- **title** — headline or repo name
- **url** — direct link
- **snippet** — excerpt or description
- **source** — which source found it
- **score** — relevance score (0–1)

## Python API

```python
from quickbrain.search import search, get_sources
from quickbrain.sources import GitHubTrending, WebFetch

# Full multi-source search
results = await search("your query", num_results=10)

# Single source
gt = GitHubTrending()
trending = await gt.search("python")

# Fetch a specific URL
wf = WebFetch()
content = await wf.search("", urls=["https://example.com"])
```

## Deduplication

QuickBrain uses smart deduplication:
1. Exact URL dedup
2. Content similarity via token/trigram Jaccard overlap (threshold 0.7)

This removes duplicate results across different sources while maximizing result diversity.

## Action Module

Import from `quickbrain.action` for post-search actions:
- `notify` — send notifications about search results
- `github` — GitHub integration for repos found in results
