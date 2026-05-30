# ============================================================
# vector_store.py
# Lightweight Vector Store Abstraction Layer
# NOW: supports file-backed embeddings + FAISS-ready design
# ============================================================

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import json
import os


# ============================================================
# VECTOR STORE
# ============================================================

class VectorStore:

    def __init__(self, embedding_dim: Optional[int] = None):

        print("🚀 Initializing Vector Store...")

        self.vectors: List[np.ndarray] = []
        self.payloads: List[Dict[str, Any]] = []

        # optional metadata
        self.embedding_dim = embedding_dim

        print("✅ Vector Store Ready.")

    # ========================================================
    # LOAD FROM EMBEDDINGS FILE (IMPORTANT FIX)
    # ========================================================

    def load_from_file(self, path: str) -> bool:

        if not os.path.exists(path):
            print(f"[WARN] Embedding file not found: {path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            embeddings = data.get("embeddings", [])
            texts = data.get("texts", [])

            if not embeddings:
                print("[WARN] No embeddings found in file")
                return False

            self.vectors = [np.array(e, dtype=np.float32) for e in embeddings]

            self.payloads = [
                {"text": t} for t in texts
            ]

            print(f"✅ Loaded {len(self.vectors)} vectors from file")

            # auto infer dimension
            if self.vectors:
                self.embedding_dim = len(self.vectors[0])

            return True

        except Exception as e:
            print(f"[ERROR] Failed to load embeddings: {e}")
            return False

    # ========================================================
    # ADD VECTOR
    # ========================================================

    def add(
        self,
        vector: np.ndarray,
        payload: Optional[Dict[str, Any]] = None
    ) -> bool:

        if vector is None:
            return False

        payload = payload or {}

        self.vectors.append(np.array(vector, dtype=np.float32))
        self.payloads.append(payload)

        return True

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        if len(self.vectors) == 0:
            return []

        results = []

        query_vector = np.array(query_vector, dtype=np.float32)

        for idx, vec in enumerate(self.vectors):

            score = self._cosine_similarity(query_vector, vec)

            results.append({
                "score": float(score),
                "text": self.payloads[idx].get("text"),
                "payload": self.payloads[idx]
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]

    # ========================================================
    # DELETE
    # ========================================================

    def delete(self, index: int) -> bool:

        if index < 0 or index >= len(self.vectors):
            return False

        self.vectors.pop(index)
        self.payloads.pop(index)

        return True

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        index: int,
        vector: Optional[np.ndarray] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> bool:

        if index < 0 or index >= len(self.vectors):
            return False

        if vector is not None:
            self.vectors[index] = np.array(vector, dtype=np.float32)

        if payload is not None:
            self.payloads[index].update(payload)

        return True

    # ========================================================
    # COSINE SIMILARITY
    # ========================================================

    def _cosine_similarity(
        self,
        a: np.ndarray,
        b: np.ndarray
    ) -> float:

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

    store = VectorStore()

    # test manual insert
    store.add(np.array([1, 0, 0]), {"text": "AI memory system"})
    store.add(np.array([0, 1, 0]), {"text": "Cybersecurity tools"})
    store.add(np.array([0, 0, 1]), {"text": "Chess strategy"})

    results = store.search(np.array([1, 0, 0]), top_k=2)

    print("\n=== VECTOR SEARCH RESULTS ===")

    for r in results:
        print(r)