# ============================================================
# memory_retriever.py
# Production-Grade Hybrid Memory Retrieval System
# FAISS + Semantic Search + Hybrid Reranking
# ============================================================

import os
import json
import threading
import logging

from datetime import datetime
from typing import List, Dict, Optional

import faiss
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)

if not logger.handlers:

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_PATH = "/root/workspace/memory_augmented_ai_assistant"

MEMORY_PATH = os.path.join(
    BASE_PATH,
    "data/raw/memory_logs/long_term_memory/memory_dataset.csv"
)

INDEX_PATH = os.path.join(
    BASE_PATH,
    "data/processed/vector_indexes/faiss_memory.index"
)

META_PATH = os.path.join(
    BASE_PATH,
    "data/processed/vector_indexes/faiss_metadata.json"
)


# ============================================================
# MEMORY RETRIEVER
# ============================================================

class MemoryRetriever:

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_cache: bool = True
    ):

        logger.info(
            "🚀 Initializing Production Memory Retriever..."
        )

        # ====================================================
        # THREAD SAFETY
        # ====================================================

        self.lock = threading.RLock()

        # ====================================================
        # CONFIG
        # ====================================================

        self.embedding_model_name = embedding_model
        self.use_cache = use_cache

        # ====================================================
        # LOAD EMBEDDING MODEL
        # ====================================================

        self.model = SentenceTransformer(
            embedding_model
        )

        # ====================================================
        # EMBEDDING DIMENSION
        # ====================================================

        self.dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        logger.info(
            f"📏 Embedding dimension: {self.dimension}"
        )

        # ====================================================
        # FAISS INDEX
        # ====================================================

        self.index = faiss.IndexFlatIP(
            self.dimension
        )

        # ====================================================
        # MEMORY STORAGE
        # ====================================================

        self.memories: List[str] = []
        self.metadata: List[Dict] = []

        # ====================================================
        # INITIALIZE
        # ====================================================

        self._initialize_index()

        logger.info(
            "✅ Memory Retriever Ready"
        )

    # ========================================================
    # INITIALIZE INDEX
    # ========================================================

    def _initialize_index(self):

        try:

            if (
                self.use_cache
                and os.path.exists(INDEX_PATH)
                and os.path.exists(META_PATH)
            ):

                self._load_cache()

            else:

                self._build_index_from_dataset()

        except Exception as e:

            logger.warning(
                f"Index initialization failed: {e}"
            )

            logger.warning(
                "⚠️ Creating empty FAISS index"
            )

            self.index = faiss.IndexFlatIP(
                self.dimension
            )

            self.memories = []
            self.metadata = []

    # ========================================================
    # LOAD CACHE
    # ========================================================

    def _load_cache(self):

        logger.info(
            "📦 Loading FAISS index from disk..."
        )

        self.index = faiss.read_index(
            INDEX_PATH
        )

        with open(
            META_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            payload = json.load(f)

        self.memories = payload.get(
            "memories",
            []
        )

        self.metadata = payload.get(
            "metadata",
            []
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        if len(self.memories) != len(self.metadata):

            raise ValueError(
                "Memory/metadata size mismatch"
            )

        if self.index.ntotal != len(self.memories):

            raise ValueError(
                "FAISS index count mismatch"
            )

        logger.info(
            f"✅ Loaded {len(self.memories)} cached memories"
        )

    # ========================================================
    # BUILD INDEX
    # ========================================================

    def _build_index_from_dataset(self):

        logger.info(
            "📊 Building FAISS index from dataset..."
        )

        if not os.path.exists(MEMORY_PATH):

            logger.warning(
                "⚠️ No memory dataset found"
            )

            return

        df = pd.read_csv(MEMORY_PATH)

        if "memory" not in df.columns:

            raise ValueError(
                "Dataset missing 'memory' column"
            )

        df = df.dropna(subset=["memory"])

        self.memories = (
            df["memory"]
            .astype(str)
            .tolist()
        )

        self.metadata = (
            df.to_dict(orient="records")
        )

        if not self.memories:

            logger.warning(
                "⚠️ Dataset empty"
            )

            return

        embeddings = self._encode(
            self.memories
        )

        self.index.add(embeddings)

        logger.info(
            f"✅ Indexed {len(self.memories)} memories"
        )

        if self.use_cache:

            self._save_cache()

    # ========================================================
    # ENCODE
    # ========================================================

    def _encode(
        self,
        texts: List[str]
    ) -> np.ndarray:

        if not texts:

            return np.empty(
                (0, self.dimension),
                dtype="float32"
            )

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        vectors = np.array(
            vectors,
            dtype=np.float32
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        if vectors.shape[1] != self.dimension:

            raise ValueError(
                f"Embedding dimension mismatch: "
                f"{vectors.shape[1]} != {self.dimension}"
            )

        # ====================================================
        # L2 NORMALIZATION
        # ====================================================

        faiss.normalize_L2(vectors)

        return vectors

    # ========================================================
    # ADD MEMORY
    # ========================================================

    def add_memory(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ):

        if not text:

            return False

        text = str(text).strip()

        if not text:

            return False

        with self.lock:

            try:

                vector = self._encode([text])

                self.index.add(vector)

                self.memories.append(text)

                self.metadata.append(
                    metadata or {}
                )

                if self.use_cache:

                    self._save_cache()

                logger.info(
                    "✅ Memory added to FAISS index"
                )

                return True

            except Exception as e:

                logger.warning(
                    f"Failed to add memory: {e}"
                )

                return False

    # ========================================================
    # RETRIEVE MEMORIES
    # ========================================================

    def retrieve_memories(
        self,
        query: str,
        top_k: int = 5,
        alpha: float = 0.7,
        beta: float = 0.2,
        gamma: float = 0.1
    ) -> List[Dict]:

        if not query:

            return []

        if self.index.ntotal == 0:

            return []

        try:

            query_vector = self._encode(
                [query]
            )

            search_k = min(
                max(top_k * 4, 10),
                self.index.ntotal
            )

            scores, indices = self.index.search(
                query_vector,
                search_k
            )

            results = []

            for score, idx in zip(
                scores[0],
                indices[0]
            ):

                if idx == -1:

                    continue

                if idx >= len(self.memories):

                    continue

                memory_text = self.memories[idx]

                meta = (
                    self.metadata[idx]
                    if idx < len(self.metadata)
                    else {}
                )

                # ============================================
                # IMPORTANCE SCORE
                # ============================================

                importance = float(
                    meta.get(
                        "importance_score",
                        meta.get(
                            "importance",
                            0.5
                        )
                    )
                )

                # ============================================
                # RECENCY SCORE
                # ============================================

                recency = (
                    self._calculate_recency_score(
                        meta
                    )
                )

                # ============================================
                # FINAL HYBRID SCORE
                # ============================================

                final_score = (
                    alpha * float(score)
                    + beta * importance
                    + gamma * recency
                )

                results.append({

                    "memory": memory_text,

                    "score": round(
                        final_score,
                        6
                    ),

                    "semantic_score": round(
                        float(score),
                        6
                    ),

                    "importance": round(
                        importance,
                        3
                    ),

                    "recency": round(
                        recency,
                        3
                    ),

                    "metadata": meta
                })

            # ================================================
            # SORT RESULTS
            # ================================================

            results.sort(
                key=lambda x: x["score"],
                reverse=True
            )

            return results[:top_k]

        except Exception as e:

            logger.warning(
                f"Retrieval failed: {e}"
            )

            return []

    # ========================================================
    # RECENCY SCORING
    # ========================================================

    def _calculate_recency_score(
        self,
        metadata: Dict
    ) -> float:

        try:

            timestamp = metadata.get(
                "timestamp"
            )

            if not timestamp:

                return 0.5

            memory_time = (
                datetime.fromisoformat(timestamp)
            )

            age_days = (
                datetime.utcnow()
                - memory_time
            ).days

            score = max(
                0.3,
                1.0 - (age_days * 0.01)
            )

            return round(score, 3)

        except Exception:

            return 0.5

    # ========================================================
    # SAVE CACHE
    # ========================================================

    def _save_cache(self):

        try:

            os.makedirs(
                os.path.dirname(INDEX_PATH),
                exist_ok=True
            )

            # ================================================
            # SAVE FAISS INDEX
            # ================================================

            faiss.write_index(
                self.index,
                INDEX_PATH
            )

            # ================================================
            # SAVE METADATA
            # ================================================

            payload = {

                "embedding_model":
                    self.embedding_model_name,

                "dimension":
                    self.dimension,

                "memory_count":
                    len(self.memories),

                "saved_at":
                    datetime.utcnow().isoformat(),

                "memories":
                    self.memories,

                "metadata":
                    self.metadata
            }

            with open(
                META_PATH,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    payload,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

        except Exception as e:

            logger.warning(
                f"Cache save failed: {e}"
            )

    # ========================================================
    # RESET INDEX
    # ========================================================

    def reset_index(self):

        with self.lock:

            self.index = faiss.IndexFlatIP(
                self.dimension
            )

            self.memories = []
            self.metadata = []

            logger.info(
                "🗑️ FAISS index reset"
            )

    # ========================================================
    # GET STATS
    # ========================================================

    def get_stats(self) -> Dict:

        return {

            "embedding_model":
                self.embedding_model_name,

            "dimension":
                self.dimension,

            "memory_count":
                len(self.memories),

            "index_size":
                self.index.ntotal,

            "cache_enabled":
                self.use_cache
        }

    # ========================================================
    # PRETTY PRINT
    # ========================================================

    def pretty_print(
        self,
        results: List[Dict]
    ):

        print("\n" + "=" * 70)
        print("🧠 RETRIEVED MEMORIES")
        print("=" * 70)

        if not results:

            print("\nNo memories found.")
            return

        for i, result in enumerate(results, 1):

            print(f"\n{i}. {result['memory']}")

            print(
                f"   hybrid_score: "
                f"{result['score']:.4f}"
            )

            print(
                f"   semantic_score: "
                f"{result['semantic_score']:.4f}"
            )

            print(
                f"   importance: "
                f"{result['importance']:.2f}"
            )

            print(
                f"   recency: "
                f"{result['recency']:.2f}"
            )

        print("\n" + "=" * 70)


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    retriever = MemoryRetriever()

    retriever.add_memory(
        "I love cybersecurity and AI",
        metadata={
            "importance": 0.9,
            "timestamp": (
                datetime.utcnow().isoformat()
            )
        }
    )

    results = retriever.retrieve_memories(
        query="artificial intelligence",
        top_k=5
    )

    retriever.pretty_print(results)

    print("\n📊 STATS")

    print(
        retriever.get_stats()
    )