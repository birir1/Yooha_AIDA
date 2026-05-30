# ============================================================
# pinecone_connector.py (SAFE + MOCK MODE)
# ============================================================

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    import pinecone
    PINECONE_AVAILABLE = True
except Exception:
    PINECONE_AVAILABLE = False
    pinecone = None
    logger.warning("Pinecone not installed → running in fallback mode")


class PineconeVectorDB:

    def __init__(
        self,
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        index_name: str = "memory-index",
        dimension: int = 384
    ):

        self.index_name = index_name
        self.dimension = dimension

        self.fallback_store = []

        if PINECONE_AVAILABLE and api_key:

            pinecone.init(
                api_key=api_key,
                environment=environment or "us-east-1"
            )

            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric="cosine"
                )

            self.index = pinecone.Index(index_name)
            self.enabled = True

            logger.info("Pinecone initialized successfully")

        else:
            self.index = None
            self.enabled = False
            logger.warning("Pinecone disabled → using fallback memory store")

    # ========================================================
    # UPSERT
    # ========================================================

    def upsert(self, vectors: List[Dict[str, Any]]):

        if self.enabled:
            self.index.upsert(vectors=vectors)
        else:
            self.fallback_store.extend(vectors)

    # ========================================================
    # QUERY
    # ========================================================

    def query(self, vector: List[float], top_k: int = 5) -> Dict[str, Any]:

        if self.enabled:
            return self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True
            )

        # fallback similarity
        def dot(a, b):
            return sum(x * y for x, y in zip(a, b))

        scored = []

        for item in self.fallback_store:
            score = dot(vector, item.get("values", []))
            scored.append((score, item))

        scored.sort(reverse=True, key=lambda x: x[0])

        top = scored[:top_k]

        return {
            "matches": [t[1] for t in top],
            "status": "fallback"
        }

    # ========================================================
    # DELETE
    # ========================================================

    def delete(self, ids: List[str]):

        if self.enabled:
            self.index.delete(ids=ids)
        else:
            self.fallback_store = [
                x for x in self.fallback_store if x.get("id") not in ids
            ]

    # ========================================================
    # HEALTH
    # ========================================================

    def health(self) -> Dict[str, Any]:

        return {
            "pinecone_enabled": self.enabled,
            "mode": "pinecone" if self.enabled else "fallback",
            "stored_vectors": len(self.fallback_store)
        }