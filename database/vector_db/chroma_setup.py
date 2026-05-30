# ============================================================
# chroma_setup.py (SAFE + FALLBACK VECTOR DB)
# ============================================================

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except Exception:
    CHROMA_AVAILABLE = False
    chromadb = None
    logger.warning("chromadb not installed → using fallback vector store")


class ChromaVectorDB:

    def __init__(
        self,
        persist_directory: str = "./data/processed/vector_indexes/chroma",
        collection_name: str = "memory"
    ):

        self.persist_directory = persist_directory
        self.collection_name = collection_name

        self.fallback_store = []

        if CHROMA_AVAILABLE:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name
            )

            logger.info("ChromaDB initialized successfully")

        else:
            self.client = None
            self.collection = None
            logger.warning("ChromaDB running in fallback mode (in-memory list)")

    # ========================================================
    # ADD DOCUMENTS
    # ========================================================

    def add(self, ids: List[str], embeddings: List[List[float]], documents: List[str], metadata: Optional[List[Dict]] = None):

        metadata = metadata or [{} for _ in documents]

        if CHROMA_AVAILABLE:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadata
            )
        else:
            for i in range(len(documents)):
                self.fallback_store.append({
                    "id": ids[i],
                    "embedding": embeddings[i],
                    "document": documents[i],
                    "metadata": metadata[i]
                })

    # ========================================================
    # QUERY
    # ========================================================

    def query(self, query_embedding: List[float], n_results: int = 5) -> Dict[str, Any]:

        if CHROMA_AVAILABLE:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

        # fallback: naive similarity (dot product proxy)
        def similarity(a, b):
            return sum(x * y for x, y in zip(a, b))

        scored = []
        for item in self.fallback_store:
            score = similarity(query_embedding, item["embedding"])
            scored.append((score, item))

        scored.sort(reverse=True, key=lambda x: x[0])

        results = scored[:n_results]

        return {
            "ids": [[r[1]["id"] for r in results]],
            "documents": [[r[1]["document"] for r in results]],
            "metadatas": [[r[1]["metadata"] for r in results]],
            "distances": [[r[0] for r in results]],
            "status": "fallback"
        }

    # ========================================================
    # DELETE
    # ========================================================

    def delete(self, ids: List[str]):

        if CHROMA_AVAILABLE:
            self.collection.delete(ids=ids)
        else:
            self.fallback_store = [
                x for x in self.fallback_store if x["id"] not in ids
            ]

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    def health(self) -> Dict[str, Any]:

        return {
            "chromadb_available": CHROMA_AVAILABLE,
            "mode": "chromadb" if CHROMA_AVAILABLE else "fallback",
            "items": len(self.fallback_store)
        }