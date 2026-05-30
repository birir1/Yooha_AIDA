# ============================================================
# analytics_cache_builder.py
# Builds analytics snapshot for fast dashboard rendering
# ============================================================

import json
import os
from memory.memory_manager import MemoryManager


class AnalyticsCacheBuilder:

    def __init__(self):
        self.memory_manager = MemoryManager()
        self.cache_path = "data/analytics_cache.json"

    def build(self):

        memories = self._get_memories()
        sessions = self._get_sessions()

        importance = {"high": 0, "medium": 0, "low": 0}
        growth = {}

        for m in memories:
            val = float(m.get("importance", 0))

            if val >= 0.7:
                importance["high"] += 1
            elif val >= 0.4:
                importance["medium"] += 1
            else:
                importance["low"] += 1

            ts = m.get("timestamp", "")
            if ts:
                day = ts[:10]
                growth[day] = growth.get(day, 0) + 1

        data = {
            "status": "ok",
            "dashboard": {
                "summary": {
                    "total_memories": len(memories),
                    "total_sessions": len(sessions),
                    "indexed_vectors": len(self.memory_manager.retriever.memories)
                },
                "charts": {
                    "importance_distribution": importance,
                    "memory_growth": growth
                },
                "system_health": {
                    "status": "healthy",
                    "db_connected": True,
                    "vector_store": True
                }
            }
        }

        os.makedirs("data", exist_ok=True)

        with open(self.cache_path, "w") as f:
            json.dump(data, f, indent=2)

        return data

    def _get_memories(self):
        try:
            return getattr(self.memory_manager.retriever, "memories", [])
        except:
            return []

    def _get_sessions(self):
        try:
            return self.memory_manager.sessions
        except:
            return {}