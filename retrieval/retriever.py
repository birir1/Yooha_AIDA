# ============================================================
# retriever.py
# Semantic Memory Retriever (Vector + DB Hybrid)
# Core retrieval engine for Memory-Augmented AI Assistant
# ============================================================

from typing import List, Dict, Any, Optional
import numpy as np


# ============================================================
# RETRIEVER
# ============================================================

class MemoryRetriever:

    def __init__(self):

        print("🚀 Initializing Memory Retriever...")

        # Lazy vector store placeholder (FAISS / Chroma / etc.)
        self.vector_index = []
        self.metadata_store = []

        print("✅ Memory Retriever Ready.")

    # ========================================================
    # ADD MEMORY TO INDEX
    # ========================================================

    def add_memory(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:

        """
        Adds memory into vector store (simplified embedding simulation)
        """

        if not text:
            return False

        metadata = metadata or {}

        embedding = self._embed(text)

        self.vector_index.append(embedding)

        self.metadata_store.append({
            "text": text,
            "embedding": embedding,
            **metadata
        })

        return True

    # ========================================================
    # RETRIEVE MEMORIES
    # ========================================================

    def retrieve_memories(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        """
        Performs similarity search over stored embeddings
        """

        if not query or not self.vector_index:
            return []

        query_vec = self._embed(query)

        scores = []

        for idx, item in enumerate(self.metadata_store):

            score = self._cosine_similarity(query_vec, item["embedding"])

            scores.append({
                "memory": item.get("text"),
                "score": score,
                "metadata": item
            })

        scores.sort(key=lambda x: x["score"], reverse=True)

        return scores[:top_k]

    # ========================================================
    # EMBEDDING (SIMULATED)
    # ========================================================

    def _embed(self, text: str) -> np.ndarray:

        """
        Lightweight deterministic embedding (no external model)
        """

        text = text.lower()

        vec = np.zeros(64)

        for i, char in enumerate(text[:64]):

            vec[i] = ord(char) % 97

        return vec

    # ========================================================
    # COSINE SIMILARITY
    # ========================================================

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:

        if a is None or b is None:
            return 0.0

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    retriever = MemoryRetriever()

    retriever.add_memory("User likes AI and machine learning")
    retriever.add_memory("User studies cybersecurity and hacking")
    retriever.add_memory("User enjoys playing chess")

    results = retriever.retrieve_memories("AI machine learning", top_k=2)

    print("\n=== RETRIEVAL RESULTS ===")
    for r in results:
        print(r)