"""Allow running QuickBrain as a module: python -m quickbrain "query" """
import sys
from quickbrain.cli import main

if "--help" in sys.argv or "-h" in sys.argv:
    print("Usage: python -m quickbrain [options] \"your query here\"")
    print()
    print("Fast, lightweight research agent.")
    print("Searches Reddit, HN, Exa, Brave, GitHub Trending in parallel.")
    print()
    print("Options:")
    print("  --json            Output as JSON instead of colored panel")
    print("  --top N           Number of results to show (default: 7)")
    print("  --watch SECONDS   Monitor query; re-check every N seconds")
    print("  --fetch URL       Fetch content from a specific URL")
    print()
    print("Examples:")
    print('  python -m quickbrain "latest open source LLM"')
    print('  python -m quickbrain "AI agent framework" --json --top 5')
    print('  python -m quickbrain "rust web frameworks" --watch 60')
    print('  python -m quickbrain --fetch "https://example.com"')
    sys.exit(0)

main()
