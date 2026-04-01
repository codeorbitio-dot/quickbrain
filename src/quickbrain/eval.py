"""
Eval harness — benchmark keyword vs embedding scoring.
"""

from __future__ import annotations

import time
from quickbrain.sources import SearchResult

# Golden queries with expected relevant terms (known-good topics)
GOLDEN_QUERIES = [
    {
        "query": "AI agent framework",
        "relevant_terms": ["agent", "framework", "llm", "autonom"],
    },
    {
        "query": "deep learning computer vision",
        "relevant_terms": ["vision", "neural", "learning", "image", "model"],
    },
    {
        "query": "react vs svelte frontend",
        "relevant_terms": ["react", "svelte", "html", "web", "component"],
    },
    {
        "query": "rust vs go performance",
        "relevant_terms": ["rust", "performance", "go", "benchmar"],
    },
    {
        "query": "python async best practice",
        "relevant_terms": ["async", "python", "concurrent"],
    },
    {
        "query": "docker compose tutorial",
        "relevant_terms": ["docker", "container", "compose"],
    },
    {
        "query": "machine learning model training",
        "relevant_terms": ["model", "train", "learning", "epoch"],
    },
    {
        "query": "kubernetes deployment yaml",
        "relevant_terms": ["kubernetes", "k8s", "deploy", "pod"],
    },
    {
        "query": "sqlite vs postgresql",
        "relevant_terms": ["sqlite", "postgres"],
    },
    {
        "query": "git rebase merge conflict",
        "relevant_terms": ["git", "rebase", "merge"],
    },
    {
        "query": "typescript generics",
        "relevant_terms": ["typescript", "generic", "type"],
    },
    {
        "query": "fastapi route handler",
        "relevant_terms": ["fastapi", "route", "handler"],
    },
    {
        "query": "redis caching strategy",
        "relevant_terms": ["redis", "cache", "ttl"],
    },
    {
        "query": "graphql query schema",
        "relevant_terms": ["graphql", "schema", "query"],
    },
    {
        "query": "nextjs static site generation",
        "relevant_terms": ["nextjs", "static", "generation", "next"],
    },
    {
        "query": "aws lambda function timeout",
        "relevant_terms": ["lambda", "aws", "timeout"],
    },
    {
        "query": "oauth2 authentication flow",
        "relevant_terms": ["oauth", "auth", "token"],
    },
    {
        "query": "webassembly performance wasm",
        "relevant_terms": ["webassembly", "wasm"],
    },
    {
        "query": "tailwind css dark mode",
        "relevant_terms": ["tailwind", "css", "dark"],
    },
    {
        "query": "open source llm benchmark",
        "relevant_terms": ["llm", "open source", "benchmar"],
    },
]


def _terms_match(text: str, terms: list[str]) -> bool:
    """Check if at least one term from `terms` appears in `text` (case-insensitive, substring)."""
    text_lower = text.lower()
    # Try full word match first, then substring
    for term in terms:
        if term.lower() in text_lower:
            return True
    return False


def precision_at_k(results: list[SearchResult], relevant_terms: list[str], k: int) -> float:
    """Fraction of top-k results that contain at least one relevant term."""
    if not results:
        return 0.0
    top_k = results[:k]
    hits = sum(1 for r in top_k if _terms_match(f"{r.title} {r.snippet}", relevant_terms))
    return hits / min(k, len(top_k))


def ndcg_at_k(results: list[SearchResult], relevant_terms: list[str], k: int) -> float:
    """NDCG@k — normalized discounted cumulative gain."""
    if not results:
        return 0.0

    # Compute relevance binary score for each result
    rels = []
    for r in results[:k]:
        match = _terms_match(f"{r.title} {r.snippet}", relevant_terms)
        rels.append(1 if match else 0)

    # DCG
    dcg = sum(r / (2 ** i) for i, r in enumerate(rels, 1))

    # Ideal DCG (all relevant at top)
    ideal = sorted(rels, reverse=True)
    idcg = sum(r / (2 ** i) for i, r in enumerate(ideal, 1))

    return dcg / idcg if idcg > 0 else 0.0


def evaluate_scorer(scorer_fn, query: str, results: list[SearchResult], relevant_terms: list[str]) -> dict:
    """Score results using a scorer function, return metrics."""
    scored = scorer_fn(query, results)
    return {
        "p@3": precision_at_k(scored, relevant_terms, 3),
        "p@5": precision_at_k(scored, relevant_terms, 5),
        "ndcg@10": ndcg_at_k(scored, relevant_terms, 10),
        "n_results": len(scored),
    }


def benchmark_scoring(results: list[SearchResult], goldens: list[dict] | None = None):
    """
    Run benchmark: compare keyword overlap vs embedding scoring.

    Returns dict with per-query metrics and aggregate summary.
    """
    from quickbrain.scorer.relevance import score_relevance as keyword_scorer
    from quickbrain.scorer.embedding import score_with_embedding as embedding_scorer

    queries = goldens or GOLDEN_QUERIES
    per_query = []
    keyword_metrics = {"p@3": [], "p@5": [], "ndcg@10": []}
    embed_metrics = {"p@3": [], "p@5": [], "ndcg@10": []}

    for g in queries:
        query = g["query"]
        terms = g["relevant_terms"]

        latencies = []
        # Keyword
        t0 = time.time()
        kw_results = evaluate_scorer(keyword_scorer, query, results, terms)
        latencies.append(time.time() - t0)

        # Embedding
        t0 = time.time()
        em_results = evaluate_scorer(embedding_scorer, query, results, terms)
        latencies.append(time.time() - t0)

        per_query.append({
            "query": query,
            "keyword": kw_results,
            "embedding": em_results,
        })
        for metric in ["p@3", "p@5", "ndcg@10"]:
            keyword_metrics[metric].append(kw_results[metric])
            embed_metrics[metric].append(em_results[metric])

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0.0

    return {
        "per_query": per_query,
        "aggregate": {
            "keyword": {k: round(avg(v), 3) for k, v in keyword_metrics.items()},
            "embedding": {k: round(avg(v), 3) for k, v in embed_metrics.items()},
        },
    }
