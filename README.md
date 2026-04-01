[![PyPI version](https://img.shields.io/badge/version-0.2.0-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

# QuickBrain

**Fast, lightweight research agent.** Get grounded summaries from across the web in 10-30 seconds — not 8 minutes.

## The Problem

Existing research agents (DeerFlow, last30days) go deep — which is great, but takes 2-8 minutes and requires half a dozen API keys. Most questions don't need that depth. You just want to know what people are saying *right now*.

## What QuickBrain Does

```
You: "latest open source LLM updates"
→ Searches Reddit, HN, Exa, Brave, GitHub Trending (parallel, ~5s)
→ Smart dedup removes duplicates across sources
→ Synthesizes 5-7 key points with real citations (~5s)
You: "action — open issue on repo X"
→ Done.
```

## Quick Start

```bash
pip install -e .

# Set at minimum one search API key (for best results)
export EXA_API_KEY="sk-..."      # free 1000/mo at exa.ai
# Optional: BRAVE_API_KEY="..."   # free 2000/mo

# Reddit and HN work out of the box — no API keys needed!
python -m quickbrain "latest open source LLM"
```

## Architecture

```
                    ┌───────────────────────────┐
                    │       CLI / API            │
                    │  --json --top --watch      │
                    └──────────────┬────────────┘
                                   │
              ┌────────────────────▼────────────┐
              │        search.py                │  ← parallel orchestrator
              │   (asyncio.gather + dedup)      │
              └────┬───┬───┬───┬───┬───────────┘
                   │   │   │   │   │
      ┌────────────┤   │   │   │   ├────────────────┐
      │            │   │   │   │   │                │
  ┌───▼───┐  ┌────▼──┐│ ┌─▼───┐│ ┌─▼───────┐ ┌────▼────┐
  │ Reddit │  │  HN   ││ │ Exa ││ │ GitHub  │ │ WebFetch│
  │ (free) │  │(free) │ │(API) │ │ Trending│ │ (free)  │
  └───┬───┘  └────┬──┘│ └─┬───┘ │ (free)  │ └────┬────┘
      │           │   │   │     └─────────┘      │
      └───────────┼───┼───┘   ┌───────────┐      │
                  │   │       │ Brave     │      │
                  │   │       │ (API)     │      │
                  │   │       └───────────┘      │
              ┌───▼───▼──┐                       │
              │  dedup.py │ ← smart dedup         │
              │ (URL +    │   (trigram/token)     │
              │  Jaccard) │                       │
              └─────┬────┘                       │
                    │                             │
              ┌─────▼──────┐                      │
              │  scorer/    │ ← relevance scoring  │
              └─────┬──────┘                      │
                    │                              │
              ┌─────▼──────┐                       │
              │ synthesize  │ ← template or LLM    │
              └─────┬──────┘                       │
                    │                               │
              ┌─────▼──────┐                        │
              │  action/    │ ← GitHub, webhook     │
              └────────────┘
```

## Sources

| Source | API Key? | Notes |
|---|---|---|
| **Reddit** | No | Public JSON, top posts & comments |
| **Hacker News** | No | Algolia search API |
| **GitHub Trending** | No | Scrapes github.com/trending — trending repos, languages, stars |
| **Exa AI** | Yes (free tier 1000/mo) | Semantic search — most impactful |
| **Brave Search** | Yes (free tier 2000/mo) | Web search backup |
| **Web Fetch** | No | Fetch and extract content from any URL |

## Smart Deduplication

QuickBrain uses a two-pass dedup strategy:

1. **URL dedup** — exact URL match (keeps the higher-scored result)
2. **Content similarity** — token + trigram Jaccard overlap between title+snippet
   - If similarity > threshold (default 0.7), drops the lower-scored result
   - Removes near-duplicates across different sources (e.g., same story on HN and Reddit)

```python
from quickbrain.dedup import smart_dedup
deduped = smart_dedup(results, threshold=0.7)
```

## Actions

After getting results, pipe them into actions:

```python
from quickbrain.action.github import GitHubIssue
from quickbrain.action.notify import WebhookNotify

# Open a GitHub issue
issue = GitHubIssue(repo="owner/repo")
await issue.execute(
    title="Research: LLM updates",
    body="Summary:\n\n1. New model released...\n2. ..."
)

# Send to webhook (Discord/Slack)
notify = WebhookNotify(url="https://hooks.slack.com/...")
await notify.execute(summary="Research results attached")
```

## CLI Usage

```bash
# Basic search (Reddit + HN + GitHub Trending, no config needed)
quickbrain "latest RAG best practices"

# With Exa (set EXA_API_KEY first)
quickbrain "new AI video generation tools 2026"

# JSON output for scripts/pipelines
quickbrain "AI agent frameworks" --json --top 5

# Monitor a query for changes
quickbrain "OpenClaw" --watch 60

# Fetch content from a URL
quickbrain --fetch "https://github.com/features/actions"

# Fetch multiple URLs
quickbrain --fetch "https://a.dev,https://b.dev" --json
```

### CLI Flags

| Flag | Description |
|---|---|
| `--json` | Output structured JSON instead of Rich panel |
| `--top N` | Number of top results to show (default: 7) |
| `--watch SECONDS` | Monitor query, re-check every N seconds, print on change |
| `--fetch URL` | Fetch and extract content from a specific URL |
| `--help` | Show help message |

### Example Output

**Normal mode:**
```
Found 23 unique results in 6.2s

Results for: latest open source LLM

1. **Sakana AI releases AI Scientist v2** [0.92]
   The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search
   https://github.com/SakanaAI/AI-Scientist-v2
   (points: 847, comments: 231)

2. **NousResearch open-sources Hermes 3 LLM**
   New 70B parameter model with strong tool-calling...
   https://nousresearch.com/hermes-3

Sources: reddit, hackernews, github_trending (23 total results)
```

**JSON mode (`--json`):**
```json
{
  "query": "AI agent frameworks",
  "sources": ["hackernews", "reddit", "github_trending", "exa"],
  "total_results": 23,
  "top": 5,
  "elapsed_s": 6.2,
  "results": [
    {
      "title": "AI Agent Framework Comparison 2026",
      "url": "https://example.com/frameworks",
      "snippet": "Comprehensive comparison of...",
      "source": "hackernews",
      "score": 0.92,
      "published": "2026-03-28T10:00:00Z",
      "metadata": {"points": 342, "comments": 89}
    }
  ]
}
```

**Watch mode (`--watch 60`):**
```
⏱ Watch mode: checking every 60s

[23:15:02] 📡 18 results
  1. New AI framework released  (github_trending)
     https://github.com/...
  2. Discussion: best agent frameworks  (reddit)
     https://reddit.com/...

[23:16:02] ✅ no change

[23:17:02] 📡 19 results (change detected)
  1. New AI framework released  (github_trending)
     https://github.com/...
  2. Hot: Agent orchestration tools  (hackernews)
     https://news.ycombinator.com/...
  3. Discussion: best agent frameworks  (reddit)
     https://reddit.com/...
```

## Adding Custom Sources

Implement the `Source` interface and register in `search.py`:

```python
from quickbrain.sources import Source, SearchResult

class MySource(Source):
    @property
    def name(self) -> str:
        return "mysource"

    def requires_config(self) -> bool:
        return False

    async def search(self, query: str, **kwargs) -> list[SearchResult]:
        # scrape or fetch here
        return [SearchResult(
            title="...",
            url="...",
            snippet="...",
            source="mysource",
        )]
```

Then add it to `get_sources()` in `search.py`.

## Python API

```python
from quickbrain.search import search, get_sources

# Full multi-source search (returns scored, deduped results)
results = await search("your query", num_results=10)

# Single source
from quickbrain.sources import GitHubTrending, WebFetch
gt = GitHubTrending()
trending = await gt.search("python")  # filter by language/name

wf = WebFetch()
content = await wf.search("", urls=["https://example.com/article"])

# Dedup
from quickbrain.dedup import smart_dedup
deduped = smart_dedup(results, threshold=0.7)
```

## Evaluation Harness

QuickBrain includes an evaluation harness for measuring search quality:

```bash
python -m quickbrain.eval
```

Metrics: precision@k, NDCG@k, per-source contribution analysis.
Configurable via `GOLDEN_QUERIES` in `eval.py`.

## OpenClaw Skill

QuickBrain ships with an OpenClaw skill package for agent integration:

```
skills/openclaw-quickbrain/
├── SKILL.md              # Skill manifest + instructions
├── scripts/
│   └── quickbrain_search.py  # Wrapper script for programmatic use
└── references/
    └── API.md            # API reference documentation
```

Use the skill from OpenClaw agents to run searches inline.

## License

MIT — see LICENSE.
