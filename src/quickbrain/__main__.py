"""Allow running QuickBrain as a module: python -m quickbrain "query" """
import sys
from quickbrain.cli import main

if "--help" in sys.argv:
    print("Usage: python -m quickbrain \"your query here\"")
    print()
    print("Fast, lightweight research agent.")
    print("Searches Reddit, HN, Exa, and Brave in parallel.")
    print()
    print("Examples:")
    print('  quickbrain "latest open source LLM"')
    print('  quickbrain "React vs Svelte 2026"')
    sys.exit(0)

main()
