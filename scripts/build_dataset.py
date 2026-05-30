import os
import pandas as pd
import json
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATHS = {
    "dialogues": os.path.join(BASE_DIR, "data/raw/conversations/multi_turn_dialogues/dialogues.csv"),
    "memory": os.path.join(BASE_DIR, "data/raw/conversations/memory_training_dataset/train.csv"),
    "go_emotions": os.path.join(BASE_DIR, "data/raw/emotional_datasets/go_emotions/train.csv"),
    "memory_logs": os.path.join(BASE_DIR, "data/raw/memory_logs/long_term_memory/memory_dataset.csv"),
}

OUTPUT_PATH = os.path.join(BASE_DIR, "data/processed/llm_finetune_dataset.jsonl")


# ============================================================
# SAFE STRING CLEANER (IMPORTANT FIX)
# ============================================================

def clean_text(x) -> str:
    if x is None:
        return ""
    if isinstance(x, float) or isinstance(x, int):
        return str(x)
    return str(x).strip()


# ============================================================
# SAFE CHAT FORMATTER
# ============================================================

def to_chat(user: str, assistant: str) -> Dict:
    user = clean_text(user)
    assistant = clean_text(assistant)

    if not user or not assistant:
        return None

    return {
        "messages": [
            {
                "role": "system",
                "content": "You are a memory-augmented emotionally intelligent assistant."
            },
            {
                "role": "user",
                "content": user
            },
            {
                "role": "assistant",
                "content": assistant
            }
        ]
    }


# ============================================================
# SAFE DATA LOADING
# ============================================================

def safe_load_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        return pd.read_csv(path, on_bad_lines="skip")
    except Exception:
        return pd.DataFrame()


# ============================================================
# DATA LOADERS (FIXED)
# ============================================================

def load_dialogues(path):
    df = safe_load_csv(path)
    samples = []

    if df.empty:
        return samples

    cols = list(df.columns)
    if len(cols) < 2:
        return samples

    for _, row in df.iterrows():
        item = to_chat(row[cols[0]], row[cols[1]])
        if item:
            samples.append(item)

    return samples


def load_memory_dataset(path):
    df = safe_load_csv(path)
    samples = []

    for _, row in df.iterrows():
        item = to_chat(
            row.get("user_input", ""),
            row.get("assistant_response", "")
        )
        if item:
            samples.append(item)

    return samples


def load_go_emotions(path):
    df = safe_load_csv(path)
    samples = []

    if "text" not in df.columns:
        return samples

    for _, row in df.iterrows():
        text = clean_text(row["text"])

        if text:
            samples.append(to_chat(
                text,
                "I understand your emotion and will respond appropriately."
            ))

    return samples


def load_memory_logs(path):
    df = safe_load_csv(path)
    samples = []

    for _, row in df.iterrows():
        item = to_chat(
            row.get("user_message", ""),
            row.get("assistant_response", "")
        )
        if item:
            samples.append(item)

    return samples


# ============================================================
# MAIN PIPELINE
# ============================================================

def build_dataset():
    print("\n🚀 Building CLEAN LLM Dataset...\n")

    dataset = []

    dataset += load_dialogues(DATA_PATHS["dialogues"])
    dataset += load_memory_dataset(DATA_PATHS["memory"])
    dataset += load_go_emotions(DATA_PATHS["go_emotions"])
    dataset += load_memory_logs(DATA_PATHS["memory_logs"])

    # FINAL SAFETY FILTER (CRITICAL)
    dataset = [
        d for d in dataset
        if d is not None
        and isinstance(d.get("messages", None), list)
    ]

    print(f"✅ Total CLEAN samples: {len(dataset)}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for item in dataset:
            try:
                json.dump(item, f)
                f.write("\n")
            except Exception:
                continue

    print(f"📦 Saved CLEAN dataset → {OUTPUT_PATH}")
    print("Done ✅")


if __name__ == "__main__":
    build_dataset()