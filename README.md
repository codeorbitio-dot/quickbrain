[![PyPI version](https://img.shields.io/badge/version-0.1.0-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

# QuickBrain

**Fast, lightweight research agent.** Get grounded summaries from across the web in 10-30 seconds — not 8 minutes.

## The Problem

Existing research agents (DeerFlow, last30days) go deep — which is great, but takes 2-8 minutes and requires half a dozen API keys. Most questions don't need that depth. You just want to know what people are saying *right now*.

## What QuickBrain Does

```
You: "Apa update terbaru LLM open source minggu ini?"
→ Searches Exa + Reddit + HN + Web (parallel, ~5s)
→ Synthesizes 3-5 key points with real citations (~5s)
You: "Buatkan summary dari poin ke-2"
→ Done.
```

## Quick Start

```bash
pip install -e .

# Set at minimum one search API key
export EXA_API_KEY="sk-..."      # free 1000/mo at exa.ai
# Optional: BRAVE_API_KEY="..."   # free 2000/mo

python -m quickbrain.search "latest open source LLM"
```

Or use as a skill in OpenClaw / Hermes / Claude Code by dropping it in your skills directory.

## Design Principles

- **Fast first.** Aim for <30s end-to-end. Depth is secondary.
- **One key to start.** Exa free tier covers most use cases. Additional sources are opt-in.
- **No GPU needed.** Runs on a $5 VPS or your laptop.
- **Research → Action.** After getting results, pipe them into actions: open a GitHub issue, send an email, schedule a reminder.

## Architecture

```
src/quickbrain/
├── __init__.py
├── cli.py              # Entry point (python -m quickbrain)
├── search.py           # Parallel multi-source search orchestrator
├── synthesize.py       # LLM-aware summarizer
├── sources/            # Pluggable data sources
│   ├── exa_search.py   # Exa AI semantic search
│   ├── brave_search.py # Brave web search
│   ├── reddit.py       # Reddit hot/top posts
│   └── hackernews.py   # Hacker News stories
├── scorer/             # Result quality scoring
│   ├── relevance.py    # Score by relevance to query
│   └── authority.py    # Score by source authority
└── action/             # Post-research actions
    ├── base.py         # Action interface
    ├── github.py       # Open GH issues/PRs
    └── notify.py       # Send via WhatsApp/email/etc
```

## Adding Sources

Implement `Source` interface and register in `sources/__init__.py`. Each source runs in parallel, results merge into a unified pipeline.

## License

MIT — see LICENSE.
