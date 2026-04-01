"""
Scorer module — relevance, embedding, and confidence scoring.
"""

from quickbrain.scorer.embedding import score_with_embedding
from quickbrain.scorer.confidence import score_with_confidence, compute_confidence
from quickbrain.scorer.relevance import score_relevance

__all__ = [
    "score_relevance",
    "score_with_embedding",
    "score_with_confidence",
    "compute_confidence",
]
