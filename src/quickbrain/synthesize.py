"""
Synthesizer — turns scored search results into a concise summary.
Uses any configured LLM, falls back to template-based if no LLM available.
"""

from __future__ import annotations

from quickbrain.sources import SearchResult


def synthesize_template(results: list[SearchResult], query: str, top_n: int = 5) -> str:
    """Generate a structured summary without an LLM. Useful as a zero-cost fallback."""
    if not results:
        return f"No results found for: {query}"

    lines = [f"Results for: {query}\n"]
    
    for i, r in enumerate(results[:top_n], 1):
        score_str = f"[{r.score:.2f}]" if r.score > 0 else ""
        lines.append(f"{i}. **{r.title}** {score_str}")
        lines.append(f"   {r.snippet[:200]}")
        lines.append(f"   {r.url}")
        if r.metadata:
            meta = ", ".join(f"{k}: {v}" for k, v in r.metadata.items())
            lines.append(f"   ({meta})")
        lines.append("")

    sources = sorted(set(r.source for r in results[:top_n]))
    lines.append(f"Sources: {', '.join(sources)} ({len(results)} total results)")
    
    return "\n".join(lines)


async def synthesize(
    results: list[SearchResult],
    query: str,
    *,
    llm_available: bool = False,
    top_n: int = 5,
) -> str:
    """
    Synthesize results into a concise summary.
    
    If llm_available=True, could call an LLM for smarter synthesis.
    Falls back to template-based output for zero-cost operation.
    """
    if llm_available:
        # Future: add LLM-based summarization here
        # via OpenAI, Gemini, Anthropic, etc.
        pass
    
    return synthesize_template(results, query, top_n=top_n)
