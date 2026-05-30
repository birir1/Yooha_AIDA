# ============================================================
# memory_manager.py
# Production Hybrid Memory Controller
# Emotionally Intelligent Memory-Augmented AI Assistant
# ============================================================

import uuid
import threading
import logging

from datetime import datetime
from typing import Dict, List, Optional, Any

from memory.db.sqlite_manager import SQLiteManager
from memory.memory_retriever import MemoryRetriever
from memory.memory_summarizer import MemorySummarizer
from memory.forgetting_mechanism import ForgettingMechanism

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
# MEMORY MANAGER
# ============================================================

class MemoryManager:

    def __init__(self):

        logger.info("🚀 Initializing Memory Manager...")

        self.lock = threading.RLock()

        self.db = SQLiteManager()
        self.retriever = MemoryRetriever()

        self._summarizer = None
        self._forgetting = None

        self.sessions: Dict[str, Dict[str, Any]] = {}

        self.max_context_messages = 8
        self.max_context_memories = 10
        self.auto_summarize_threshold = 25

        logger.info("✅ Memory Manager Ready")

    # ============================================================
    # 🔥 REAL IMPORTANCE ENGINE (FIXED)
    # ============================================================

    def calculate_importance(self, text: str, emotion: Optional[str]) -> float:

        if not text:
            return 0.3

        text = text.lower()

        score = 0.3

        # High-value keywords (important memories)
        high_keywords = [
            "remember", "important", "goal", "dream", "future",
            "career", "study", "research", "project", "ai",
            "cybersecurity", "machine learning", "system"
        ]

        medium_keywords = [
            "like", "prefer", "enjoy", "work", "build",
            "learn", "use", "create"
        ]

        for k in high_keywords:
            if k in text:
                score += 0.25

        for k in medium_keywords:
            if k in text:
                score += 0.10

        # Emotion boost
        emotion_boost = {
            "joy": 0.1,
            "love": 0.2,
            "sadness": 0.15,
            "anger": 0.1,
            "fear": 0.2,
            "stress": 0.2,
            "anxiety": 0.25,
            "excitement": 0.15
        }

        if emotion:
            score += emotion_boost.get(emotion.lower(), 0)

        return round(min(score, 1.0), 3)

    # ============================================================
    # MEMORY TYPE DETECTION (IMPROVED)
    # ============================================================

    def detect_memory_type(self, text: str) -> str:

        text = text.lower()

        if any(k in text for k in ["goal", "future", "dream"]):
            return "future_goal"

        if any(k in text for k in ["study", "school", "learn", "research"]):
            return "education"

        if any(k in text for k in ["love", "like", "prefer", "enjoy"]):
            return "preference"

        if any(k in text for k in ["family", "friend"]):
            return "relationship"

        if any(k in text for k in ["sad", "angry", "stress", "fear"]):
            return "emotional"

        return "general"

    # ============================================================
    # STORE INTERACTION
    # ============================================================

    def store_interaction(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        emotion: Optional[str] = None
    ) -> bool:

        try:

            self.db.add_message(session_id=session_id, role="user", content=user_message)
            self.db.add_message(session_id=session_id, role="assistant", content=assistant_response)

            importance = self.calculate_importance(user_message, emotion)
            memory_type = self.detect_memory_type(user_message)

            # 🔥 CRITICAL FIX: store REAL importance
            self.db.add_memory(
                session_id=session_id,
                memory=user_message,
                memory_type=memory_type,
                importance=importance,
                emotion=emotion
            )

            self._store_vector_memory(
                session_id,
                user_message,
                memory_type,
                importance,
                emotion
            )

            return True

        except Exception as e:
            logger.exception(f"store_interaction failed: {e}")
            return False

    # ============================================================
    # VECTOR STORAGE (FIXED importance propagation)
    # ============================================================

    def _store_vector_memory(
        self,
        session_id,
        text,
        memory_type,
        importance,
        emotion
    ):
        try:
            self.retriever.add_memory(
                text=text,
                metadata={
                    "session_id": session_id,
                    "memory_type": memory_type,
                    "importance": float(importance),
                    "emotion": emotion,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Vector storage failed: {e}")

    # ============================================================
    # ANALYTICS SUPPORT
    # ============================================================

    def get_all_memories(self):
        """
        FIX: analytics compatibility layer
        """
        try:
            if hasattr(self.db, "get_all_memories"):
                return self.db.get_all_memories()

            if hasattr(self.db, "get_memories"):
                return self.db.get_memories()

            return []

        except Exception:
            return []

    def get_memory_statistics(self) -> Dict:

        try:
            db_stats = {}

            if hasattr(self.db, "get_stats"):
                db_stats = self.db.get_stats()

            memories = self.get_all_memories()

            return {
                "active_sessions": len(self.sessions),
                "total_memories": len(memories),
                "database_stats": db_stats
            }

        except Exception as e:
            logger.exception(f"get_memory_statistics failed: {e}")
            return {}

    # ============================================================
    # RETRIEVAL
    # ============================================================

    def retrieve_memory(self, session_id, query, top_k=5):
        try:
            return self.retriever.retrieve_memories(query=query, top_k=top_k)
        except Exception:
            return []

    # ============================================================
    # OPTIONAL PLACEHOLDERS
    # ============================================================

    def summarizer(self):
        return None

    def forgetting(self):
        return None

    def build_context_window(self, session_id, retrieved_memories):
        return ""

    def summarize_session(self, session_id):
        return None

    def apply_forgetting(self):
        return None

    def get_history(self, session_id):
        return []

    def delete_session(self, session_id):
        self.sessions.pop(session_id, None)

    def health_check(self):
        return {"status": "healthy"}