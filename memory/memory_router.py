# ============================================================
# memory_router.py
# Memory Routing Layer (API-safe abstraction)
# Bridges API ↔ MemoryManager ↔ DB ↔ Retriever
# ============================================================

import logging
from typing import Dict, Any, List, Optional

from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


# ============================================================
# MEMORY ROUTER
# ============================================================

class MemoryRouter:

    def __init__(self, memory_manager: Optional[MemoryManager] = None):

        logger.info("🚀 Initializing Memory Router...")

        self.memory_manager = memory_manager or MemoryManager()

        logger.info("✅ Memory Router Ready")

    # ========================================================
    # STORE INTERACTION
    # ========================================================

    def store(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        emotion: Optional[str] = None
    ) -> bool:

        try:
            return self.memory_manager.store_interaction(
                session_id=session_id,
                user_message=user_message,
                assistant_response=assistant_response,
                emotion=emotion
            )

        except Exception as e:
            logger.exception(f"[MemoryRouter] store failed: {e}")
            return False

    # ========================================================
    # RETRIEVE MEMORY (HYBRID SEARCH)
    # ========================================================

    def retrieve(
        self,
        session_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        try:
            return self.memory_manager.retrieve_memory(
                session_id=session_id,
                query=query,
                top_k=top_k
            )

        except Exception as e:
            logger.exception(f"[MemoryRouter] retrieve failed: {e}")
            return []

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    def build_context(
        self,
        session_id: str,
        memories: List[Dict[str, Any]]
    ) -> str:

        try:
            return self.memory_manager.build_context_window(
                session_id=session_id,
                retrieved_memories=memories
            )

        except Exception as e:
            logger.exception(f"[MemoryRouter] context build failed: {e}")
            return ""

    # ========================================================
    # SESSION MANAGEMENT
    # ========================================================

    def create_session(self, user_id: str = "anonymous") -> str:

        try:
            return self.memory_manager.create_session(user_id)

        except Exception as e:
            logger.exception(f"[MemoryRouter] session creation failed: {e}")
            return f"session_{user_id}"

    # ========================================================
    # HISTORY
    # ========================================================

    def history(self, session_id: str) -> List[Dict[str, Any]]:

        try:
            return self.memory_manager.get_history(session_id)

        except Exception as e:
            logger.exception(f"[MemoryRouter] history failed: {e}")
            return []

    # ========================================================
    # DELETE SESSION
    # ========================================================

    def delete_session(self, session_id: str) -> bool:

        try:
            self.memory_manager.delete_session(session_id)
            return True

        except Exception as e:
            logger.exception(f"[MemoryRouter] delete session failed: {e}")
            return False

    # ========================================================
    # STATISTICS
    # ========================================================

    def stats(self) -> Dict[str, Any]:

        try:
            return self.memory_manager.get_memory_statistics()

        except Exception as e:
            logger.exception(f"[MemoryRouter] stats failed: {e}")
            return {}

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    def health(self) -> Dict[str, Any]:

        try:
            return self.memory_manager.health_check()

        except Exception as e:
            logger.exception(f"[MemoryRouter] health failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    router = MemoryRouter()

    session = router.create_session("test_user")

    router.store(
        session_id=session,
        user_message="I love cybersecurity",
        assistant_response="That's great!",
        emotion="joy"
    )

    memories = router.retrieve(
        session_id=session,
        query="cybersecurity"
    )

    print("\n=== MEMORIES ===")
    print(memories)

    print("\n=== CONTEXT ===")
    print(router.build_context(session, memories))

    print("\n=== HEALTH ===")
    print(router.health())