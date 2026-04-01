"""
CLI entry point for QuickBrain.
Usage: python -m quickbrain "your query here"
"""

from __future__ import annotations

import sys
import time
import asyncio

from rich.console import Console
from rich.panel import Panel

from quickbrain.search import search, get_sources
from quickbrain.synthesize import synthesize


console = Console()


def main() -> None:
    query = " ".join(sys.argv[1:])
    if not query:
        console.print("[bold red]Usage:[/bold red] quickbrain \"your query here\"")
        sys.exit(1)

    sources = get_sources()
    source_names = [s.name for s in sources]
    console.print(f"[dim]QuickBrain — searching with: {', '.join(source_names)}[/dim]")
    console.print()

    start = time.time()

    results = asyncio.run(search(query, num_results=15))
    elapsed = time.time() - start

    console.print(f"[dim]Found {len(results)} unique results in {elapsed:.1f}s[/dim]\n")

    summary = asyncio.run(synthesize(results, query, top_n=7))
    console.print(Panel(summary, title="🧠 QuickBrain", border_style="blue"))


if __name__ == "__main__":
    main()
