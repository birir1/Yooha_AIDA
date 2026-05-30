# ============================================================
# forgetting_mechanism.py
# Production-Grade Adaptive Memory Forgetting System
# Cognitive Lifecycle + Retention + Pruning Engine
# ============================================================

import os
import json
import pandas as pd

from datetime import datetime, timedelta
from typing import Optional, Dict, List


# ============================================================
# FORGETTING MECHANISM
# ============================================================

class ForgettingMechanism:

    def __init__(self):

        print("🚀 Initializing Forgetting Mechanism...")

        # ====================================================
        # PATHS
        # ====================================================

        self.project_root = (
            "/root/workspace/"
            "memory_augmented_ai_assistant"
        )

        self.memory_path = (
            f"{self.project_root}/"
            "data/raw/memory_logs/"
            "long_term_memory/"
            "memory_dataset.csv"
        )

        self.archive_path = (
            f"{self.project_root}/"
            "data/raw/memory_logs/"
            "archives/"
            "archived_memories.csv"
        )

        # ====================================================
        # RETENTION CONFIG
        # ====================================================

        self.default_importance_threshold = 0.45

        self.default_decay_rate = 0.01

        self.default_retention_days = 30

        self.max_memory_limit = 10000

        # SAFETY:
        # never delete more than 95%
        self.min_keep_ratio = 0.05

        print("✅ Forgetting Mechanism Ready.")

    # ========================================================
    # LOAD DATABASE
    # ========================================================

    def load_database(self) -> pd.DataFrame:

        if not os.path.exists(self.memory_path):

            return pd.DataFrame()

        try:

            df = pd.read_csv(self.memory_path)

            if df.empty:

                return df

            # =================================================
            # REQUIRED COLUMNS
            # =================================================

            required = {

                "session_id": "",

                "memory": "",

                "importance_score": 0.5,

                "timestamp": datetime.utcnow().isoformat(),

                "memory_type": "general_memory",

                "metadata": "{}"
            }

            for col, default in required.items():

                if col not in df.columns:

                    df[col] = default

            return df

        except Exception as e:

            print(
                f"[WARN] Failed loading memory DB: {e}"
            )

            return pd.DataFrame()

    # ========================================================
    # SAVE DATABASE
    # ========================================================

    def save_database(
        self,
        df: pd.DataFrame
    ):

        try:

            os.makedirs(
                os.path.dirname(self.memory_path),
                exist_ok=True
            )

            df.to_csv(
                self.memory_path,
                index=False
            )

            return True

        except Exception as e:

            print(
                f"[WARN] Failed saving DB: {e}"
            )

            return False

    # ========================================================
    # ARCHIVE MEMORIES
    # ========================================================

    def archive_memories(
        self,
        memories: pd.DataFrame
    ):

        if memories.empty:
            return

        try:

            os.makedirs(
                os.path.dirname(self.archive_path),
                exist_ok=True
            )

            if os.path.exists(self.archive_path):

                existing = pd.read_csv(
                    self.archive_path
                )

                combined = pd.concat(
                    [existing, memories],
                    ignore_index=True
                )

            else:

                combined = memories

            combined.to_csv(
                self.archive_path,
                index=False
            )

        except Exception as e:

            print(
                f"[WARN] Archive failed: {e}"
            )

    # ========================================================
    # IMPORTANCE DECAY
    # ========================================================

    def apply_memory_decay(
        self,
        decay_rate: Optional[float] = None
    ) -> Dict:

        decay_rate = (
            decay_rate
            or self.default_decay_rate
        )

        df = self.load_database()

        if df.empty:

            return {
                "status": "empty_database"
            }

        now = datetime.utcnow()

        updated_scores = []

        for _, row in df.iterrows():

            try:

                ts = pd.to_datetime(
                    row.get("timestamp"),
                    errors="coerce"
                )

                if pd.isna(ts):

                    updated_scores.append(
                        float(
                            row.get(
                                "importance_score",
                                0.5
                            )
                        )
                    )

                    continue

                days_old = (
                    now - ts
                ).days

                current = float(
                    row.get(
                        "importance_score",
                        0.5
                    )
                )

                # ============================================
                # DECAY CURVE
                # ============================================

                decayed = (
                    current -
                    (days_old * decay_rate)
                )

                # SAFE CLAMP
                decayed = max(
                    0.0,
                    round(decayed, 4)
                )

                updated_scores.append(
                    decayed
                )

            except Exception:

                updated_scores.append(
                    float(
                        row.get(
                            "importance_score",
                            0.5
                        )
                    )
                )

        df["importance_score"] = (
            updated_scores
        )

        self.save_database(df)

        return {

            "status": "decay_applied",

            "total_processed": len(df),

            "decay_rate": decay_rate
        }

    # ========================================================
    # DUPLICATE REMOVAL
    # ========================================================

    def remove_duplicates(self) -> Dict:

        df = self.load_database()

        if df.empty:

            return {
                "status": "empty_database"
            }

        before = len(df)

        if "memory" not in df.columns:

            return {
                "status": "missing_memory_column"
            }

        # ====================================================
        # NORMALIZE
        # ====================================================

        df["memory_normalized"] = (
            df["memory"]
            .astype(str)
            .str.lower()
            .str.strip()
        )

        # KEEP HIGHEST IMPORTANCE
        df = (
            df.sort_values(
                by="importance_score",
                ascending=False
            )
            .drop_duplicates(
                subset=["memory_normalized"]
            )
        )

        df = df.drop(
            columns=["memory_normalized"]
        )

        after = len(df)

        self.save_database(df)

        return {

            "status": "duplicates_removed",

            "removed": before - after,

            "remaining": after
        }

    # ========================================================
    # CLEAN OLD MEMORIES
    # ========================================================

    def clean_old_memories(
        self,
        session_id: Optional[str] = None,
        days_threshold: Optional[int] = None,
        importance_threshold: Optional[float] = None
    ) -> Dict:

        days_threshold = (
            days_threshold
            or self.default_retention_days
        )

        importance_threshold = (
            importance_threshold
            or self.default_importance_threshold
        )

        df = self.load_database()

        if df.empty:

            return {
                "status": "empty_database"
            }

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        cutoff = (
            datetime.utcnow() -
            timedelta(days=days_threshold)
        )

        original_size = len(df)

        keep_mask = []

        archived_rows = []

        for _, row in df.iterrows():

            keep = True

            try:

                # ============================================
                # SESSION FILTER
                # ============================================

                if session_id:

                    if str(
                        row.get("session_id")
                    ) != str(session_id):

                        keep_mask.append(True)

                        continue

                importance = float(
                    row.get(
                        "importance_score",
                        0
                    )
                )

                timestamp = row.get(
                    "timestamp"
                )

                if pd.isna(timestamp):

                    keep_mask.append(True)

                    continue

                # ============================================
                # FORGET RULE
                # ============================================

                if (
                    importance <
                    importance_threshold
                    and timestamp < cutoff
                ):

                    keep = False

                    archived_rows.append(row)

            except Exception:

                keep = True

            keep_mask.append(keep)

        cleaned = df[keep_mask]

        # ====================================================
        # SAFETY CHECK
        # ====================================================

        min_allowed = max(
            1,
            int(original_size * self.min_keep_ratio)
        )

        if len(cleaned) < min_allowed:

            return {

                "status": "blocked",

                "reason":
                    "safety_threshold_triggered"
            }

        # ====================================================
        # ARCHIVE REMOVED MEMORIES
        # ====================================================

        if archived_rows:

            archive_df = pd.DataFrame(
                archived_rows
            )

            self.archive_memories(
                archive_df
            )

        removed = (
            original_size -
            len(cleaned)
        )

        self.save_database(cleaned)

        return {

            "status": "cleaned",

            "removed": removed,

            "remaining": len(cleaned),

            "archived": len(archived_rows)
        }

    # ========================================================
    # LIMIT TOTAL MEMORY SIZE
    # ========================================================

    def keep_top_memories(
        self,
        top_n: Optional[int] = None
    ) -> Dict:

        top_n = top_n or self.max_memory_limit

        df = self.load_database()

        if df.empty:

            return {
                "status": "empty_database"
            }

        before = len(df)

        df = df.sort_values(
            by="importance_score",
            ascending=False
        )

        kept = df.head(top_n)

        removed_df = df.iloc[top_n:]

        # ARCHIVE REMOVED
        if not removed_df.empty:

            self.archive_memories(
                removed_df
            )

        self.save_database(kept)

        return {

            "status": "trimmed",

            "before": before,

            "remaining": len(kept),

            "archived": len(removed_df)
        }

    # ========================================================
    # MEMORY STATISTICS
    # ========================================================

    def statistics(self) -> Dict:

        df = self.load_database()

        if df.empty:

            return {

                "total_memories": 0,

                "average_importance": 0,

                "max_importance": 0,

                "min_importance": 0
            }

        scores = pd.to_numeric(
            df["importance_score"],
            errors="coerce"
        ).fillna(0)

        return {

            "total_memories":
                int(len(df)),

            "average_importance":
                round(float(scores.mean()), 4),

            "max_importance":
                round(float(scores.max()), 4),

            "min_importance":
                round(float(scores.min()), 4),

            "memory_types":
                (
                    df["memory_type"]
                    .value_counts()
                    .to_dict()
                    if "memory_type"
                    in df.columns
                    else {}
                )
        }

    # ========================================================
    # FULL FORGETTING PIPELINE
    # ========================================================

    def run_full_forgetting_cycle(self) -> Dict:

        print(
            "🧠 Running forgetting cycle..."
        )

        decay = self.apply_memory_decay()

        dedup = self.remove_duplicates()

        clean = self.clean_old_memories()

        trim = self.keep_top_memories()

        stats = self.statistics()

        report = {

            "status": "completed",

            "timestamp":
                datetime.utcnow().isoformat(),

            "pipeline": {

                "decay": decay,

                "deduplication": dedup,

                "cleanup": clean,

                "trimming": trim
            },

            "statistics": stats
        }

        print(
            "✅ Forgetting cycle completed."
        )

        return report


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    fm = ForgettingMechanism()

    print("\n=== INITIAL STATS ===")
    print(
        fm.statistics()
    )

    print("\n=== RUNNING CYCLE ===")

    result = (
        fm.run_full_forgetting_cycle()
    )

    print(result)

    print("\n=== FINAL STATS ===")
    print(
        fm.statistics()
    )