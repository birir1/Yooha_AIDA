# ============================================================
# train_embeddings.py
# Train/Generate Embeddings for Memory-Augmented AI System
# Uses sentence-transformers for semantic vector creation
# ============================================================

import os
import json
from typing import List, Dict, Any

import torch
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# ============================================================
# EMBEDDING TRAINER / GENERATOR
# ============================================================

class EmbeddingTrainer:

    def __init__(self):

        print("🚀 Loading embedding model...")

        self.model = SentenceTransformer(MODEL_NAME)

        print("✅ Embedding model ready.")

    # ========================================================
    # ENCODE TEXTS
    # ========================================================

    def encode(self, texts: List[str]):

        if not texts:
            return []

        return self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_tensor=False,
            normalize_embeddings=True
        )

    # ========================================================
    # LOAD DATASET
    # ========================================================

    def load_dataset(self, path: str) -> List[str]:

        if not os.path.exists(path):
            print(f"[WARN] Dataset not found: {path}")
            return []

        texts = []

        try:

            if path.endswith(".csv"):

                import csv

                with open(path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)

                    for row in reader:
                        texts.append(" ".join(row))

            elif path.endswith(".json"):

                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for item in data:
                    if isinstance(item, dict):
                        texts.append(item.get("text", ""))
                    else:
                        texts.append(str(item))

            elif path.endswith(".txt"):

                with open(path, "r", encoding="utf-8") as f:
                    texts = [line.strip() for line in f if line.strip()]

        except Exception as e:
            print(f"[ERROR] Failed loading dataset: {e}")

        return texts

    # ========================================================
    # SAVE EMBEDDINGS
    # ========================================================

    def save_embeddings(self, embeddings, texts: List[str], output_path: str):

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        data = {
            "texts": texts,
            "embeddings": embeddings.tolist()
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        print(f"💾 Saved embeddings -> {output_path}")

    # ========================================================
    # PIPELINE
    # ========================================================

    def run(self, dataset_path: str, output_path: str):

        print("🚀 Running embedding training pipeline...")

        texts = self.load_dataset(dataset_path)

        if not texts:
            print("[WARN] No texts found.")
            return

        embeddings = self.encode(texts)

        self.save_embeddings(embeddings, texts, output_path)

        print("✅ Embedding pipeline complete.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    trainer = EmbeddingTrainer()

    trainer.run(
        dataset_path="data/raw/conversations/memory_training_dataset/train.csv",
        output_path="data/processed/embeddings/trained_embeddings.json"
    )