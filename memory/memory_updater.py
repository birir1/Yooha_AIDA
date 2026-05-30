# ============================================================
# memory_updater.py
# Production Memory Ingestion + Sync Layer
# ============================================================

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from memory.db.sqlite_manager import SQLiteManager


# ============================================================
# PATHS
# ============================================================

MEMORY_PATH = (
    "/root/workspace/memory_augmented_ai_assistant/"
    "data/raw/memory_logs/long_term_memory/memory_dataset.csv"
)


# ============================================================
# MEMORY UPDATER (PRODUCTION CORE)
# ============================================================

class MemoryUpdater:

    def __init__(self):

        print("🚀 Initializing Memory Updater...")

        self.db = SQLiteManager()

        os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)

        # ensure CSV exists (fallback layer only)
        if not os.path.exists(MEMORY_PATH):
            df = pd.DataFrame(columns=[
                "session_id",
                "timestamp",
                "memory",
                "emotion",
                "importance_score",
                "memory_type",
                "metadata"
            ])
            df.to_csv(MEMORY_PATH, index=False)

        print("✅ Memory Updater Ready")

    # ========================================================
    # MAIN API (FIXED FOR MEMORY MANAGER)
    # ========================================================

    def add_memory(
        self,
        session_id: str,
        memory: str,
        memory_type: str = "general_memory",
        importance_score: float = 0.5,
        emotion: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):

        """
        FIX: accepts ONLY explicit parameters (no 'interaction' dict anymore)
        """

        timestamp = datetime.utcnow().isoformat()

        meta_json = json.dumps(metadata or {})

        # ----------------------------------------------------
        # 1. WRITE TO SQLITE (PRIMARY STORE)
        # ----------------------------------------------------
        try:
            self.db.add_memory(
                session_id=session_id,
                memory=memory,
                memory_type=memory_type,
                importance=importance_score,
                emotion=emotion,
                metadata=meta_json,
                timestamp=timestamp
            )
        except Exception as e:
            print(f"⚠️ DB write failed: {e}")

        # ----------------------------------------------------
        # 2. WRITE TO CSV (FALLBACK / DEBUG)
        # ----------------------------------------------------
        try:
            df = pd.read_csv(MEMORY_PATH)

            new_row = {
                "session_id": session_id,
                "timestamp": timestamp,
                "memory": memory,
                "emotion": emotion,
                "importance_score": importance_score,
                "memory_type": memory_type,
                "metadata": meta_json
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(MEMORY_PATH, index=False)

        except Exception as e:
            print(f"⚠️ CSV write failed: {e}")

        return True

    # ========================================================
    # BULK IMPORT (SAFE)
    # ========================================================

    def bulk_import(self, memories: List[Dict]):

        df = pd.DataFrame(memories)

        if os.path.exists(MEMORY_PATH):
            existing = pd.read_csv(MEMORY_PATH)
            df = pd.concat([existing, df], ignore_index=True)

        df.to_csv(MEMORY_PATH, index=False)

    # ========================================================
    # LOAD DATABASE
    # ========================================================

    def load_memories(self):

        if not os.path.exists(MEMORY_PATH):
            return pd.DataFrame()

        return pd.read_csv(MEMORY_PATH)

    # ========================================================
    # SESSION FILTER
    # ========================================================

    def load_session_memories(self, session_id: str):

        df = self.load_memories()

        if df.empty:
            return df

        return df[df["session_id"] == session_id]

    # ========================================================
    # STATISTICS (PRODUCTION MONITORING)
    # ========================================================

    def memory_statistics(self):

        df = self.load_memories()

        if df.empty:
            return {
                "total_memories": 0,
                "unique_sessions": 0,
                "memory_types": {}
            }

        return {
            "total_memories": len(df),
            "unique_sessions": df["session_id"].nunique(),
            "memory_types": df["memory_type"].value_counts().to_dict(),
            "avg_importance": float(df["importance_score"].mean())
        }