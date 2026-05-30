# ============================================================
# seed_memory_dataset.py
# AI Memory Dataset Seeder (Analytics + Dashboard Fix)
# ============================================================

import random
from datetime import datetime, timedelta

from memory.db.sqlite_manager import SQLiteManager


db = SQLiteManager()

# ------------------------------------------------------------
# SAMPLE MEMORY BANK (REALISTIC AI INTERACTIONS)
# ------------------------------------------------------------

MEMORY_BANK = [
    "User asked about cybersecurity fundamentals",
    "Explained how SQL injection works in web apps",
    "User showed interest in FAISS vector databases",
    "Discussed transformer architecture for NLP models",
    "User is building a memory-augmented AI system",
    "Explained Flask backend routing issues",
    "User is debugging analytics dashboard",
    "Discussed importance of embeddings in retrieval systems",
    "User wants real-time AI memory visualization",
    "Explained SQLite vs vector store tradeoffs",
    "User working on capstone AI project",
    "Discussed FAISS indexing optimization",
    "User asked about hallucination in LLMs",
    "Explained retrieval augmented generation (RAG)",
    "User building Flask + React dashboard",
    "Debugging API route failures in analytics module",
    "User exploring memory summarization techniques",
    "Discussed forgetting mechanisms in AI systems",
    "User integrating persistent memory layer",
    "Explained importance scoring in memory systems"
]

EMOTIONS = ["neutral", "curious", "focused", "confused", "excited"]

# ------------------------------------------------------------
# SEED CONFIG
# ------------------------------------------------------------

NUM_ENTRIES = 120


def random_timestamp(days_back=14):
    """Generate realistic timestamps across last 14 days"""
    now = datetime.utcnow()
    delta_days = random.randint(0, days_back)
    delta_seconds = random.randint(0, 86400)

    return (now - timedelta(days=delta_days, seconds=delta_seconds)).isoformat()


def random_importance():
    """Create realistic skewed importance distribution"""
    r = random.random()

    if r < 0.15:
        return round(random.uniform(0.75, 1.0), 2)   # HIGH
    elif r < 0.45:
        return round(random.uniform(0.4, 0.74), 2)   # MEDIUM
    else:
        return round(random.uniform(0.0, 0.39), 2)   # LOW


# ------------------------------------------------------------
# SEED EXECUTION
# ------------------------------------------------------------

def seed():
    print("\n🚀 Starting Memory Dataset Seeding...\n")

    session_id = "seed-session-001"
    user_id = "demo-user"

    db.create_session_if_not_exists(session_id, user_id)

    for i in range(NUM_ENTRIES):

        memory = random.choice(MEMORY_BANK)
        importance = random_importance()
        timestamp = random_timestamp()

        # insert memory
        db._execute(
            """
            INSERT INTO memories
            (session_id, memory, memory_type, importance, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                memory,
                "general",
                importance,
                '{"source":"seed"}',
                timestamp,
                timestamp
            )
        )

        if i % 20 == 0:
            print(f"✔ Inserted {i}/{NUM_ENTRIES}")

    print("\n✅ Seeding Complete!")
    print(f"📦 Total Entries Added: {NUM_ENTRIES}")
    print("📊 Your dashboard should now show real analytics.\n")


if __name__ == "__main__":
    seed()