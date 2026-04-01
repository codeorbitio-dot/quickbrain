#!/usr/bin/env python3
"""
QuickBrain Search Wrapper — runs `python -m quickbrain` and formats output.

Usage:
    python quickbrain_search.py "your query"
    python quickbrain_search.py "your query" --json
    python quickbrain_search.py "your query" --top 5
"""

import sys
import subprocess
import json


def run(query: str, json_output: bool = False, top: int = 7) -> str:
    """Run quickbrain search and return formatted output."""
    cmd = [sys.executable, "-m", "quickbrain", query, "--top", str(top)]
    if json_output:
        cmd.append("--json")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Error: search timed out after 60s"
    except Exception as e:
        return f"Error: {e}"


def fetch_url(url: str, json_output: bool = False) -> str:
    """Fetch content from a specific URL."""
    cmd = [sys.executable, "-m", "quickbrain", "--fetch", url]
    if json_output:
        cmd.append("--json")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def main():
    if len(sys.argv) < 2:
        print("Usage: quickbrain_search.py \"query\" [--json] [--top N]")
        print("       quickbrain_search.py --fetch URL [--json]")
        sys.exit(1)

    query = sys.argv[1]
    json_output = "--json" in sys.argv
    top = 7
    if "--top" in sys.argv:
        idx = sys.argv.index("--top")
        if idx + 1 < len(sys.argv):
            top = int(sys.argv[idx + 1])

    if query == "--fetch" and len(sys.argv) > 2:
        print(fetch_url(sys.argv[2], json_output))
    else:
        print(run(query, json_output, top))


if __name__ == "__main__":
    main()
