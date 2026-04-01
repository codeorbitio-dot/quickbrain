[![PyPI version](https://img.shields.io/badge/version-0.1.0-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

# QuickBrain

**Fast, lightweight research agent.** Get grounded summaries from across the web in 10-30 seconds — not 8 minutes.

## The Problem

Existing research agents (DeerFlow, last30days) go deep — which is great, but takes 2-8 minutes and requires half a dozen API keys. Most questions don't need that depth. You just want to know what people are saying *right now*.

## What QuickBrain Does

```
You: "latest open source LLM updates"
→ Searches Reddit, HN, Exa, Brave (parallel, ~5s)
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
                    ┌──────────────┐
                    │   CLI / API   │
                    └──────┬───────┘
                           │
              ┌────────────▼────────────┐
              │     search.py           │  ← parallel orchestrator
              │   (asyncio.gather)      │
              └────┬───┬───┬───┬───────┘
                   │   │   │   │
      ┌────────────┤   │   │   ├────────────┐
      │            │   │   │   │            │
  ┌───▼───┐  ┌────▼──┐│ ┌─▼───┐│ ┌────────▼┐│
  │ Reddit │  │  HN   ││ │ Exa ││ │ Brave   ││
  │ (free) │  │(free) │ │(API) │ │ (API)   │ │
  └───┬───┘  └────┬──┘│ └─┬───┘│ └────────┘││
      │           │   │   │   │             │
      └───────────┼───┼───┘   └─────────────┘
                  │   │
              ┌───▼───▼──┐
              │ scorer/   │  ← relevance scoring
              └─────┬────┘
                    │
              ┌─────▼──────┐
              │ synthesize │  ← template or LLM summary
              └─────┬──────┘
                    │
              ┌─────▼──────┐
              │ action/     │  ← GitHub, webhook, notify
              └────────────┘
```

## Sources

| Source | API Key? | Notes |
|---|---|---|
| **Reddit** | No | Public JSON, top posts & comments |
| **Hacker News** | No | Algolia search API |
| **Exa AI** | Yes (free tier 1000/mo) | Semantic search — most impactful |
| **Brave Search** | Yes (free tier 2000/mo) | Web search backup |

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
# Basic search (Reddit + HN, no config needed)
quickbrain "latest RAG best practices"

# With Exa (set EXA_API_KEY first)
quickbrain "new AI video generation tools 2026"
```

### Example Output

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

Sources: reddit, hackernews (23 total results)
```

## Adding Custom Sources

Implement the `Source` interface and register in `search.py`:

```python
from quickbrain.sources import Source, SearchResult

class MySource(Source):
    @property
    def name(self) -> str:
        return "mysource"

    async def search(self, query: str, **kwargs) -> list[SearchResult]:
        # scrape or fetch here
        return [SearchResult(...)]
```

## License

MIT — see LICENSE.
