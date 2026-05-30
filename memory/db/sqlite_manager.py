# ============================================================
# sqlite_manager.py
# Production-Grade SQLite Memory Database Layer (FIXED + ANALYTICS READY)
# ============================================================

import os
import sqlite3
import threading
from datetime import datetime
from typing import Any


class SQLiteManager:

    def __init__(self, db_path: str = "/root/workspace/memory_augmented_ai_assistant/data/memory.db"):

        self.lock = threading.Lock()
        self.db_path = db_path

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )

        self.conn.row_factory = sqlite3.Row

        self._configure_database()
        self._create_tables()
        self._create_indexes()

        print(f"✅ SQLiteManager initialized: {self.db_path}")

    # ========================================================
    # CONFIG
    # ========================================================

    def _configure_database(self):
        cursor = self.conn.cursor()

        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA cache_size=10000;")
        cursor.execute("PRAGMA foreign_keys=ON;")

        self.conn.commit()

    # ========================================================
    # SAFE EXECUTOR
    # ========================================================

    def _execute(
        self,
        query: str,
        params: tuple = (),
        fetch: bool = False,
        fetchone: bool = False
    ) -> Any:

        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute(query, params)
                self.conn.commit()

                if fetchone:
                    row = cursor.fetchone()
                    return dict(row) if row else None

                if fetch:
                    rows = cursor.fetchall()
                    return [dict(r) for r in rows]

                return True

            except Exception as e:
                self.conn.rollback()
                print(f"[SQLITE ERROR] {e}")
                return None

    # ========================================================
    # TABLES
    # ========================================================

    def _create_tables(self):

        self._execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            created_at TEXT
        )
        """)

        self._execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
        """)

        self._execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            memory TEXT,
            memory_type TEXT,
            importance REAL,
            metadata TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """)

    # ========================================================
    # INDEXES
    # ========================================================

    def _create_indexes(self):

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)",
            "CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)"
        ]

        for q in indexes:
            self._execute(q)

    # ========================================================
    # SESSION
    # ========================================================

    def create_session_if_not_exists(self, session_id: str, user_id: str = "anonymous"):

        existing = self._execute(
            "SELECT session_id FROM sessions WHERE session_id=?",
            (session_id,),
            fetchone=True
        )

        if existing:
            return True

        return self._execute(
            "INSERT INTO sessions VALUES (?, ?, ?)",
            (session_id, user_id, datetime.utcnow().isoformat())
        )

    # ========================================================
    # MESSAGES
    # ========================================================

    def add_message(self, session_id: str, role: str, content: str):

        if not content:
            return False

        self.create_session_if_not_exists(session_id)

        return self._execute(
            """
            INSERT INTO messages
            (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, datetime.utcnow().isoformat())
        )

    # ========================================================
    # MEMORIES
    # ========================================================

    def add_memory(
        self,
        session_id: str,
        memory: str,
        memory_type: str = "general",
        importance: float = 0.5,
        metadata: str = "{}"
    ):

        if not memory:
            return False

        self.create_session_if_not_exists(session_id)

        return self._execute(
            """
            INSERT INTO memories
            (session_id, memory, memory_type, importance, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                memory,
                memory_type,
                float(importance),
                metadata,
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat()
            )
        )

    # ========================================================
    # ✅ FIX: GET ALL MEMORIES (MISSING BEFORE → CAUSED ANALYTICS ISSUES)
    # ========================================================

    def get_all_memories(self, limit: int = 1000):
        """
        FIXED: Used by analytics dashboard + retriever bridge
        """

        rows = self._execute(
            """
            SELECT session_id, memory, memory_type, importance, metadata, created_at
            FROM memories
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
            fetch=True
        ) or []

        # normalize types for analytics
        cleaned = []

        for r in rows:
            cleaned.append({
                "session_id": r.get("session_id"),
                "text": r.get("memory", ""),
                "memory_type": r.get("memory_type", "general"),
                "importance": float(r.get("importance") or 0),
                "metadata": r.get("metadata", "{}"),
                "timestamp": r.get("created_at") or ""
            })

        return cleaned

    # ========================================================
    # GETTERS
    # ========================================================

    def get_messages(self, session_id: str, limit: int = 20):

        return self._execute(
            """
            SELECT role, content, timestamp
            FROM messages
            WHERE session_id=?
            ORDER BY id ASC
            LIMIT ?
            """,
            (session_id, limit),
            fetch=True
        ) or []

    def get_memories(self, session_id: str, limit: int = 50):

        return self._execute(
            """
            SELECT memory, memory_type, importance, created_at
            FROM memories
            WHERE session_id=?
            ORDER BY importance DESC
            LIMIT ?
            """,
            (session_id, limit),
            fetch=True
        ) or []

    def search_memories(self, query: str, limit: int = 10):

        return self._execute(
            """
            SELECT memory, importance, created_at
            FROM memories
            WHERE memory LIKE ?
            ORDER BY importance DESC
            LIMIT ?
            """,
            (f"%{query}%", limit),
            fetch=True
        ) or []

    # ========================================================
    # STATS (SAFE)
    # ========================================================

    def get_stats(self):

        def safe_count(sql):
            res = self._execute(sql, fetchone=True)
            return res["c"] if res else 0

        return {
            "sessions": safe_count("SELECT COUNT(*) as c FROM sessions"),
            "messages": safe_count("SELECT COUNT(*) as c FROM messages"),
            "memories": safe_count("SELECT COUNT(*) as c FROM memories")
        }

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):
        try:
            self.conn.close()
            print("✅ DB closed")
        except Exception as e:
            print(f"[WARN] DB close failed: {e}")