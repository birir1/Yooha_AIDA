# ============================================================
# generate_embeddings.py
# Embedding Generation Pipeline for Memory-Augmented AI System
# Converts raw memory/text datasets into vector representations
# ============================================================

import os
import json
import numpy as np
from typing import List, Dict, Any


# ============================================================
# SIMPLE EMBEDDING ENGINE (LIGHTWEIGHT FALLBACK)
# ============================================================

class SimpleEmbedder:

    def __init__(self, dim: int = 64):

        print("🚀 Initializing Simple Embedder...")

        self.dim = dim

        print(f"✅ Embedder Ready (dim={dim})")

    # ========================================================
    # EMBED SINGLE TEXT
    # ========================================================

    def embed(self, text: str) -> np.ndarray:

        vec = np.zeros(self.dim)

        text = text.lower()

        for i, char in enumerate(text[:self.dim]):

            vec[i] = (ord(char) % 97) / 97.0

        return vec

    # ========================================================
    # EMBED BATCH
    # ========================================================

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:

        return [self.embed(t) for t in texts]


# ============================================================
# DATA LOADER
# ============================================================

def load_texts_from_file(file_path: str) -> List[str]:

    texts = []

    if not os.path.exists(file_path):
        print(f"[WARN] File not found: {file_path}")
        return texts

    try:

        if file_path.endswith(".json"):

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):

                for item in data:

                    if isinstance(item, dict):

                        texts.append(item.get("text", ""))
                    else:

                        texts.append(str(item))

        elif file_path.endswith(".txt"):

            with open(file_path, "r", encoding="utf-8") as f:
                texts = [line.strip() for line in f if line.strip()]

        elif file_path.endswith(".csv"):

            import csv

            with open(file_path, "r", encoding="utf-8") as f:

                reader = csv.reader(f)

                for row in reader:

                    texts.append(" ".join(row))

    except Exception as e:

        print(f"[ERROR] Failed to load {file_path}: {e}")

    return texts


# ============================================================
# SAVE EMBEDDINGS
# ============================================================

def save_embeddings(
    output_path: str,
    embeddings: List[np.ndarray],
    texts: List[str]
):

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = {
        "embeddings": [e.tolist() for e in embeddings],
        "texts": texts
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    print(f"💾 Embeddings saved to {output_path}")


# ============================================================
# PIPELINE RUNNER
# ============================================================

def run_embedding_pipeline(input_path: str, output_path: str):

    print("\n🚀 Running Embedding Pipeline...")

    embedder = SimpleEmbedder(dim=64)

    texts = load_texts_from_file(input_path)

    if not texts:
        print("[WARN] No texts found. Exiting.")
        return

    embeddings = embedder.embed_batch(texts)

    save_embeddings(output_path, embeddings, texts)

    print("✅ Embedding pipeline completed.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    # Example paths (adjust for your dataset)
    input_file = "data/raw/conversations/memory_training_dataset/train.csv"
    output_file = "data/processed/embeddings/memory_embeddings.json"

    run_embedding_pipeline(input_file, output_file)