# ============================================================
# semantic_search.py
# Semantic Search Engine (Hybrid Lightweight + Extendable)
# Used for memory + document retrieval ranking
# ============================================================

from typing import List, Dict, Any
import numpy as np
import re


# ============================================================
# SEMANTIC SEARCH ENGINE
# ============================================================

class SemanticSearch:

    def __init__(self):

        print("🚀 Initializing Semantic Search Engine...")

        self.dim = 64

        print("✅ Semantic Search Ready.")

    # ========================================================
    # MAIN SEARCH FUNCTION
    # ========================================================

    def search(
        self,
        query: str,
        corpus: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        """
        Returns ranked results from corpus based on semantic similarity
        """

        if not query or not corpus:
            return []

        query_vec = self._embed(query)

        results = []

        for item in corpus:

            text = (
                item.get("text")
                or item.get("memory")
                or item.get("content")
                or ""
            )

            if not text:
                continue

            score = self._similarity(query_vec, self._embed(text))

            results.append({
                "text": text,
                "score": score,
                "metadata": item
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]

    # ========================================================
    # EMBEDDING (LIGHTWEIGHT HEURISTIC)
    # ========================================================

    def _embed(self, text: str) -> np.ndarray:

        """
        Deterministic pseudo-embedding (no external model)
        """

        vec = np.zeros(self.dim)

        text = text.lower()

        words = re.findall(r"\w+", text)

        for i, w in enumerate(words[: self.dim]):

            for j, c in enumerate(w[:3]):

                vec[(i + j) % self.dim] += (ord(c) % 97)

        return vec

    # ========================================================
    # SIMILARITY FUNCTION
    # ========================================================

    def _similarity(self, a: np.ndarray, b: np.ndarray) -> float:

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    engine = SemanticSearch()

    corpus = [
        {"text": "User loves artificial intelligence and ML"},
        {"text": "User is interested in cybersecurity"},
        {"text": "User enjoys playing chess"},
        {"text": "User builds AI assistants with memory"}
    ]

    results = engine.search("AI and machine learning", corpus, top_k=3)

    print("\n=== SEARCH RESULTS ===")

    for r in results:
        print(r)