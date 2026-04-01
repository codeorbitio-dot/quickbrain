"""
CLI entry point for QuickBrain.
Usage:
    python -m quickbrain "your query here"
    python -m quickbrain "query" --json --top 5
    python -m quickbrain "query" --watch 30
    python -m quickbrain --fetch "https://example.com/article"
"""

from __future__ import annotations

import sys
import time
import json
import argparse
import hashlib

import asyncio

from rich.console import Console
from rich.panel import Panel

from quickbrain.search import search, get_sources
from quickbrain.synthesize import synthesize
from quickbrain.sources.web_fetch import WebFetch
from quickbrain.sources import SearchResult


console = Console()


# ── Helpers ──────────────────────────────────────────────

def _result_dict(r: SearchResult) -> dict:
    """Convert a SearchResult to a JSON-serializable dict."""
    return {
        "title": r.title,
        "url": r.url,
        "snippet": r.snippet,
        "source": r.source,
        "score": round(r.score, 4),
        "published": r.published,
        "metadata": r.metadata,
    }


def _results_signature(results: list[SearchResult], top_n: int) -> str:
    """Deterministic hash of top-N results for change detection in --watch mode."""
    data = json.dumps([_result_dict(r) for r in results[:top_n]], sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()[:16]


# ── Modes ────────────────────────────────────────────────

def _do_fetch(urls: list[str], json_output: bool) -> None:
    """Fetch content from specific URLs using the web_fetch source."""
    console.print(f"[dim]QuickBrain — fetching {len(urls)} URL(s) ...[/dim]\n")

    source = WebFetch()
    results = asyncio.run(source.search("", urls=urls))

    if json_output:
        print(json.dumps({"source": "web_fetch", "urls": urls,
                          "results": [_result_dict(r) for r in results]}, indent=2))
        return

    for i, r in enumerate(results, 1):
        console.print(f"[bold cyan]{i}. {r.title}[/bold cyan]")
        console.print(f"   [dim]{r.url}[/dim]")
        console.print(f"   {r.snippet[:300] or '(empty)'}")
        console.print()


def _do_search(query: str, top_n: int, json_output: bool) -> list[SearchResult]:
    """Run a normal search and display results."""
    sources = get_sources()
    source_names = [s.name for s in sources]
    console.print(f"[dim]QuickBrain — searching with: {', '.join(source_names)}[/dim]\n")

    start = time.time()
    # Fetch more than we need so scoring has enough material
    results = asyncio.run(search(query, num_results=max(15, top_n * 3)))
    elapsed = time.time() - start
    top = results[:top_n]

    if json_output:
        out = {
            "query": query,
            "sources": source_names,
            "total_results": len(results),
            "top": top_n,
            "elapsed_s": round(elapsed, 1),
            "results": [_result_dict(r) for r in top],
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return results

    console.print(f"[dim]Found {len(results)} unique results in {elapsed:.1f}s "
                  f"(showing top {top_n})[/dim]\n")

    summary = asyncio.run(synthesize(top, query, top_n=top_n))
    console.print(Panel(summary, title="🧠 QuickBrain", border_style="blue"))
    return results


def _do_watch(query: str, interval: int, top_n: int, json_output: bool) -> None:
    """Monitor a query and print when results change."""
    console.print(f"[bold cyan]⏱ Watch mode: checking every {interval}s[/bold cyan]")
    prev_sig = ""
    prev_count = 0
    try:
        while True:
            results = asyncio.run(search(query, num_results=max(15, top_n * 3)))
            sig = _results_signature(results, top_n)

            if sig != prev_sig:
                ts = time.strftime("%H:%M:%S")
                delta = f"{len(results)} results"
                if prev_sig:
                    delta += " (change detected)"
                console.print(f"\n[{ts}] 📡 {delta}")

                top = results[:top_n]
                if json_output:
                    print(json.dumps({
                        "time": ts, "total": len(results), "top": top_n,
                        "results": [_result_dict(r) for r in top],
                    }, indent=2, ensure_ascii=False))
                else:
                    for i, r in enumerate(top, 1):
                        console.print(f"  [bold]{i}. {r.title}[/bold]  [dim]{r.source}[/dim]")
                        console.print(f"     [dim]{r.url}[/dim]")
                console.print()

                prev_sig = sig
                prev_count = len(results)
            else:
                console.print(f"[{time.strftime('%H:%M:%S')}] ✅ no change")

            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[dim]Watch mode stopped.[/dim]")


# ── Arg parsing ──────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="quickbrain",
        description="Fast web research agent — search Reddit, HN, Exa, GitHub Trending.",
    )
    p.add_argument("query", nargs="*", help="Search query")
    p.add_argument("--json", action="store_true", dest="json_output",
                   help="Output results as JSON instead of Rich panel")
    p.add_argument("--top", type=int, default=7,
                   help="Number of top results to show (default: 7)")
    p.add_argument("--watch", type=int, default=0, metavar="SECONDS",
                   help="Monitor query; re-check every N seconds, print on change")
    p.add_argument("--fetch", type=str, metavar="URL",
                   help="Fetch content from a URL (comma-separated for multiple)")
    return p


# ── Main ─────────────────────────────────────────────────

def main(cli_args: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(cli_args)

    # --fetch mode
    if args.fetch:
        urls = [u.strip() for u in args.fetch.split(",") if u.strip()]
        return _do_fetch(urls, args.json_output)

    # Query required for search or watch
    if not args.query:
        console.print("[bold red]Usage:[/bold red] quickbrain \"your query\"")
        sys.exit(1)

    query = " ".join(args.query)

    # --watch mode
    if args.watch and args.watch > 0:
        return _do_watch(query, args.watch, args.top, args.json_output)

    # Normal search
    _do_search(query, args.top, args.json_output)


if __name__ == "__main__":
    main()