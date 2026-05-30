# ============================================================
# reranker.py
# Retrieval Reranking Module for Memory-Augmented AI Assistant
# Re-scores retrieved candidates using hybrid heuristics
# ============================================================

from typing import List, Dict, Any
import numpy as np
import re


# ============================================================
# RERANKER
# ============================================================

class Reranker:

    def __init__(self):

        print("🚀 Initializing Reranker...")

        # weighting strategy for hybrid reranking
        self.weights = {
            "semantic": 0.5,
            "recency": 0.2,
            "importance": 0.2,
            "keyword_overlap": 0.1
        }

        print("✅ Reranker Ready.")

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        """
        Reorder retrieved memory/corpus results by relevance
        """

        if not candidates:
            return []

        scored = []

        for item in candidates:

            score = self._compute_score(query, item)

            item_copy = dict(item)
            item_copy["rerank_score"] = score

            scored.append(item_copy)

        # sort by final score
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)

        return scored[:top_k]

    # ========================================================
    # SCORE COMPUTATION
    # ========================================================

    def _compute_score(self, query: str, item: Dict[str, Any]) -> float:

        text = (
            item.get("memory")
            or item.get("text")
            or item.get("content")
            or ""
        )

        semantic_score = self._semantic_similarity(query, text)

        keyword_score = self._keyword_overlap(query, text)

        recency_score = self._recency_score(item)

        importance_score = float(item.get("importance", 0.5))

        final_score = (
            semantic_score * self.weights["semantic"] +
            keyword_score * self.weights["keyword_overlap"] +
            recency_score * self.weights["recency"] +
            importance_score * self.weights["importance"]
        )

        return float(np.clip(final_score, 0.0, 1.0))

    # ========================================================
    # SEMANTIC SIMILARITY (lightweight heuristic)
    # ========================================================

    def _semantic_similarity(self, query: str, text: str) -> float:

        q_tokens = set(query.lower().split())
        t_tokens = set(text.lower().split())

        if not q_tokens or not t_tokens:
            return 0.0

        overlap = len(q_tokens & t_tokens)
        union = len(q_tokens | t_tokens)

        return overlap / union if union > 0 else 0.0

    # ========================================================
    # KEYWORD OVERLAP BOOST
    # ========================================================

    def _keyword_overlap(self, query: str, text: str) -> float:

        query_words = set(re.findall(r"\w+", query.lower()))
        text_words = set(re.findall(r"\w+", text.lower()))

        if not query_words:
            return 0.0

        overlap = query_words.intersection(text_words)

        return len(overlap) / len(query_words)

    # ========================================================
    # RECENCY SCORE
    # ========================================================

    def _recency_score(self, item: Dict[str, Any]) -> float:

        # expects ISO timestamp or fallback metadata
        timestamp = item.get("timestamp") or item.get("metadata", {}).get("timestamp")

        if not timestamp:
            return 0.5

        try:
            # simple heuristic: newer = higher score
            # we avoid full datetime parsing dependency for robustness
            if isinstance(timestamp, str):

                # crude recency heuristic based on string patterns
                if "2026" in timestamp:
                    return 1.0
                if "2025" in timestamp:
                    return 0.8
                if "2024" in timestamp:
                    return 0.6

        except:
            pass

        return 0.5


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    reranker = Reranker()

    query = "learn AI machine learning"

    candidates = [
        {"memory": "User likes AI", "importance": 0.9, "timestamp": "2026-01-01"},
        {"memory": "User studies cybersecurity", "importance": 0.6, "timestamp": "2025-01-01"},
        {"memory": "User enjoys chess", "importance": 0.3}
    ]

    result = reranker.rerank(query, candidates, top_k=3)

    print("\n=== RERANKED RESULTS ===")
    for r in result:
        print(r)