# ============================================================
# memory_service.py
# Production Memory Service
# Handles memory storage, retrieval, ranking, and formatting
# ============================================================

import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)

# ============================================================
# MEMORY SERVICE
# ============================================================

class MemoryService:

    def __init__(
        self,
        db_manager=None,
        vector_store=None,
        embedding_model=None
    ):

        self.db = db_manager
        self.vector_store = vector_store
        self.embedding_model = embedding_model

        logger.info("✅ MemoryService initialized")

    # ========================================================
    # SESSION MANAGEMENT
    # ========================================================

    def create_session(
        self,
        user_id: str
    ) -> str:

        session_id = str(uuid.uuid4())

        try:

            if (
                self.db and
                hasattr(self.db, "create_session")
            ):

                self.db.create_session(
                    session_id=session_id,
                    user_id=user_id
                )

        except Exception as e:

            logger.exception(
                "Failed to create session"
            )

        return session_id

    # ========================================================
    # STORE MEMORY
    # ========================================================

    def store_memory(
        self,
        session_id: str,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        try:

            memory_id = str(uuid.uuid4())

            timestamp = datetime.utcnow().isoformat()

            metadata = metadata or {}

            # =================================================
            # CREATE EMBEDDING
            # =================================================

            embedding = None

            if self.embedding_model:

                try:

                    if hasattr(
                        self.embedding_model,
                        "encode"
                    ):

                        embedding = (
                            self.embedding_model
                            .encode(content)
                        )

                        if hasattr(
                            embedding,
                            "tolist"
                        ):
                            embedding = embedding.tolist()

                except Exception:
                    logger.exception(
                        "Embedding generation failed"
                    )

            # =================================================
            # SAVE TO SQLITE
            # =================================================

            if (
                self.db and
                hasattr(self.db, "store_memory")
            ):

                self.db.store_memory(
                    memory_id=memory_id,
                    session_id=session_id,
                    role=role,
                    content=content,
                    metadata=metadata,
                    timestamp=timestamp
                )

            # =================================================
            # SAVE TO VECTOR DB
            # =================================================

            if (
                self.vector_store and
                embedding is not None
            ):

                try:

                    if hasattr(
                        self.vector_store,
                        "add"
                    ):

                        self.vector_store.add(
                            ids=[memory_id],
                            embeddings=[embedding],
                            documents=[content],
                            metadatas=[{
                                "session_id": session_id,
                                "role": role,
                                "timestamp": timestamp
                            }]
                        )

                    elif hasattr(
                        self.vector_store,
                        "upsert"
                    ):

                        self.vector_store.upsert(
                            vectors=[{
                                "id": memory_id,
                                "values": embedding,
                                "metadata": {
                                    "session_id": session_id,
                                    "role": role,
                                    "content": content,
                                    "timestamp": timestamp
                                }
                            }]
                        )

                except Exception:
                    logger.exception(
                        "Vector DB storage failed"
                    )

            logger.info(
                f"💾 Memory stored: {memory_id}"
            )

            return {
                "status": "success",
                "memory_id": memory_id,
                "session_id": session_id,
                "timestamp": timestamp
            }

        except Exception as e:

            logger.exception(
                "Failed to store memory"
            )

            return {
                "status": "error",
                "message": str(e)
            }

    # ========================================================
    # STORE INTERACTION
    # ========================================================

    def store_interaction(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        emotion: Optional[str] = None
    ):

        self.store_memory(
            session_id=session_id,
            content=user_message,
            role="user",
            metadata={
                "emotion": emotion
            }
        )

        self.store_memory(
            session_id=session_id,
            content=assistant_response,
            role="assistant",
            metadata={
                "emotion": emotion
            }
        )

    # ========================================================
    # RETRIEVE MEMORIES
    # ========================================================

    def retrieve_memories(
        self,
        session_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        try:

            # =================================================
            # EMBEDDING SEARCH
            # =================================================

            query_embedding = None

            if self.embedding_model:

                try:

                    if hasattr(
                        self.embedding_model,
                        "encode"
                    ):

                        query_embedding = (
                            self.embedding_model
                            .encode(query)
                        )

                        if hasattr(
                            query_embedding,
                            "tolist"
                        ):
                            query_embedding = (
                                query_embedding.tolist()
                            )

                except Exception:
                    logger.exception(
                        "Query embedding failed"
                    )

            # =================================================
            # VECTOR SEARCH
            # =================================================

            if (
                self.vector_store and
                query_embedding is not None
            ):

                try:

                    # =============================
                    # CHROMA STYLE
                    # =============================

                    if hasattr(
                        self.vector_store,
                        "query"
                    ):

                        results = (
                            self.vector_store.query(
                                query_embeddings=[
                                    query_embedding
                                ],
                                n_results=top_k
                            )
                        )

                        memories = []

                        docs = results.get(
                            "documents",
                            [[]]
                        )[0]

                        metas = results.get(
                            "metadatas",
                            [[]]
                        )[0]

                        distances = results.get(
                            "distances",
                            [[]]
                        )[0]

                        for i in range(
                            len(docs)
                        ):

                            metadata = (
                                metas[i]
                                if i < len(metas)
                                else {}
                            )

                            if (
                                metadata.get(
                                    "session_id"
                                ) != session_id
                            ):
                                continue

                            memories.append({
                                "content": docs[i],
                                "score": float(
                                    1 - distances[i]
                                )
                                if i < len(distances)
                                else 0.0,
                                "metadata": metadata
                            })

                        return memories

                    # =============================
                    # PINECONE STYLE
                    # =============================

                    elif hasattr(
                        self.vector_store,
                        "search"
                    ):

                        results = (
                            self.vector_store.search(
                                vector=query_embedding,
                                top_k=top_k
                            )
                        )

                        memories = []

                        for match in results:

                            metadata = match.get(
                                "metadata",
                                {}
                            )

                            if (
                                metadata.get(
                                    "session_id"
                                ) != session_id
                            ):
                                continue

                            memories.append({
                                "content":
                                    metadata.get(
                                        "content",
                                        ""
                                    ),
                                "score":
                                    match.get(
                                        "score",
                                        0.0
                                    ),
                                "metadata":
                                    metadata
                            })

                        return memories

                except Exception:
                    logger.exception(
                        "Vector retrieval failed"
                    )

            # =================================================
            # FALLBACK DATABASE SEARCH
            # =================================================

            if (
                self.db and
                hasattr(self.db, "get_session_memories")
            ):

                rows = (
                    self.db.get_session_memories(
                        session_id=session_id,
                        limit=top_k
                    )
                )

                memories = []

                for row in rows:

                    memories.append({
                        "id": row.get("id"),
                        "content":
                            row.get("content", ""),
                        "role":
                            row.get("role", "user"),
                        "timestamp":
                            row.get("timestamp"),
                        "score": 0.5
                    })

                return memories

            return []

        except Exception as e:

            logger.exception(
                "Memory retrieval failed"
            )

            return []

    # ========================================================
    # BUILD CONTEXT WINDOW
    # ========================================================

    def build_context_window(
        self,
        session_id: str,
        retrieved_memories: List[Dict[str, Any]],
        max_chars: int = 4000
    ) -> str:

        try:

            context_parts = []

            current_size = 0

            # =================================================
            # RECENT SESSION MEMORIES
            # =================================================

            if (
                self.db and
                hasattr(self.db, "get_recent_memories")
            ):

                recent = (
                    self.db.get_recent_memories(
                        session_id=session_id,
                        limit=10
                    )
                )

                for memory in recent:

                    role = memory.get(
                        "role",
                        "user"
                    )

                    content = memory.get(
                        "content",
                        ""
                    )

                    block = (
                        f"{role.upper()}: "
                        f"{content}"
                    )

                    if (
                        current_size +
                        len(block)
                    ) > max_chars:
                        break

                    context_parts.append(block)

                    current_size += len(block)

            # =================================================
            # RETRIEVED MEMORIES
            # =================================================

            if retrieved_memories:

                context_parts.append(
                    "\nRELEVANT MEMORIES:"
                )

                for memory in retrieved_memories:

                    content = memory.get(
                        "content",
                        ""
                    )

                    block = f"- {content}"

                    if (
                        current_size +
                        len(block)
                    ) > max_chars:
                        break

                    context_parts.append(block)

                    current_size += len(block)

            return "\n".join(
                context_parts
            )

        except Exception:

            logger.exception(
                "Context building failed"
            )

            return ""

    # ========================================================
    # MEMORY STATS
    # ========================================================

    def get_stats(self) -> Dict[str, Any]:

        stats = {
            "database_connected":
                self.db is not None,

            "vector_store_connected":
                self.vector_store is not None,

            "embedding_model_loaded":
                self.embedding_model is not None
        }

        try:

            if (
                self.db and
                hasattr(self.db, "get_stats")
            ):

                db_stats = self.db.get_stats()

                stats.update(db_stats)

        except Exception:
            logger.exception(
                "Failed to fetch stats"
            )

        return stats

    # ========================================================
    # DELETE SESSION
    # ========================================================

    def delete_session(
        self,
        session_id: str
    ) -> bool:

        try:

            if (
                self.db and
                hasattr(self.db, "delete_session")
            ):

                self.db.delete_session(
                    session_id
                )

            logger.info(
                f"🗑 Session deleted: {session_id}"
            )

            return True

        except Exception:

            logger.exception(
                "Failed to delete session"
            )

            return False