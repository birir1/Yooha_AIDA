# ============================================================
# train_emotion_model.py
# PRODUCTION EMOTION TRAINER
# Compact GoEmotions CSV Compatible
# ============================================================

import os
import gc
import torch
import pandas as pd

from typing import List, Tuple

from torch.utils.data import Dataset

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

# ============================================================
# GPU SETTINGS
# ============================================================

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

torch.backends.cuda.matmul.allow_tf32 = True

# ============================================================
# CONFIG
# ============================================================

BASE_MODEL = "j-hartmann/emotion-english-distilroberta-base"

DATASET_PATH = (
    "/root/workspace/memory_augmented_ai_assistant/"
    "data/raw/emotional_datasets/go_emotions/train.csv"
)

OUTPUT_DIR = (
    "/root/workspace/memory_augmented_ai_assistant/"
    "models/emotion_detection/classifier"
)

MAX_LENGTH = 96
MAX_SAMPLES = 50000

# ============================================================
# TARGET LABELS
# ============================================================

LABELS = [
    "anger",
    "disgust",
    "fear",
    "joy",
    "neutral",
    "sadness",
    "surprise"
]

LABEL2ID = {
    label: idx
    for idx, label in enumerate(LABELS)
}

# ============================================================
# GOEMOTIONS LABEL IDS
# ============================================================

GOEMOTION_ID_MAP = {
    0: "admiration",
    1: "amusement",
    2: "anger",
    3: "annoyance",
    4: "approval",
    5: "caring",
    6: "confusion",
    7: "curiosity",
    8: "desire",
    9: "disappointment",
    10: "disapproval",
    11: "disgust",
    12: "embarrassment",
    13: "excitement",
    14: "fear",
    15: "gratitude",
    16: "grief",
    17: "joy",
    18: "love",
    19: "nervousness",
    20: "optimism",
    21: "pride",
    22: "realization",
    23: "relief",
    24: "remorse",
    25: "sadness",
    26: "surprise",
    27: "neutral"
}

# ============================================================
# REDUCED EMOTION MAP
# ============================================================

REDUCED_MAP = {
    "anger": "anger",
    "annoyance": "anger",
    "disapproval": "anger",

    "disgust": "disgust",

    "fear": "fear",
    "nervousness": "fear",

    "joy": "joy",
    "amusement": "joy",
    "approval": "joy",
    "caring": "joy",
    "desire": "joy",
    "excitement": "joy",
    "gratitude": "joy",
    "love": "joy",
    "optimism": "joy",
    "pride": "joy",
    "relief": "joy",
    "admiration": "joy",

    "sadness": "sadness",
    "disappointment": "sadness",
    "embarrassment": "sadness",
    "grief": "sadness",
    "remorse": "sadness",

    "surprise": "surprise",
    "realization": "surprise",
    "confusion": "surprise",
    "curiosity": "surprise",

    "neutral": "neutral"
}

# ============================================================
# DATASET
# ============================================================

class EmotionDataset(Dataset):

    def __init__(
        self,
        texts,
        labels,
        tokenizer,
        max_len=MAX_LENGTH
    ):

        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):

        text = str(self.texts[idx])

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )

        return {
            "input_ids":
                encoding["input_ids"].squeeze(0),

            "attention_mask":
                encoding["attention_mask"].squeeze(0),

            "labels":
                torch.tensor(
                    self.labels[idx],
                    dtype=torch.long
                )
        }

# ============================================================
# TRAINER
# ============================================================

class EmotionTrainer:

    def __init__(self):

        print("🚀 Loading tokenizer and model...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL
        )

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(
                BASE_MODEL,
                num_labels=len(LABELS)
            )
        )

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model.to(self.device)

        print("✅ Emotion model ready.")
        print(f"✅ Device: {self.device}")

    # ========================================================
    # LOAD DATA
    # ========================================================

    def load_data(
        self,
        path: str
    ) -> Tuple[List[str], List[int]]:

        print("🚀 Reading dataset...")

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        df = pd.read_csv(path)

        print(f"✅ Raw rows: {len(df)}")
        print(f"✅ Original columns: {df.columns.tolist()}")

        # ====================================================
        # FIX DATASET HEADERS
        # ====================================================

        if list(df.columns) == ['0', '1', '2']:

            df.columns = [
                "text",
                "emotion_id",
                "sample_id"
            ]

        print(f"✅ Fixed columns: {df.columns.tolist()}")

        texts = []
        labels = []

        for _, row in df.iterrows():

            text = str(row["text"]).strip()

            if not text:
                continue

            try:
                emotion_id = int(row["emotion_id"])

            except Exception:
                emotion_id = 27

            goemotion = GOEMOTION_ID_MAP.get(
                emotion_id,
                "neutral"
            )

            reduced_emotion = REDUCED_MAP.get(
                goemotion,
                "neutral"
            )

            final_label = LABEL2ID[reduced_emotion]

            texts.append(text)

            labels.append(final_label)

            if len(texts) >= MAX_SAMPLES:
                break

        print(f"✅ Final samples: {len(texts)}")

        return texts, labels

    # ========================================================
    # TRAIN
    # ========================================================

    def train(self):

        texts, labels = self.load_data(DATASET_PATH)

        dataset = EmotionDataset(
            texts,
            labels,
            self.tokenizer
        )

        args = TrainingArguments(
            output_dir=OUTPUT_DIR,

            per_device_train_batch_size=4,

            gradient_accumulation_steps=4,

            learning_rate=2e-5,

            num_train_epochs=1,

            logging_steps=25,

            save_steps=500,

            save_total_limit=2,

            report_to="none",

            remove_unused_columns=False,

            dataloader_pin_memory=False
        )

        trainer = Trainer(
            model=self.model,
            args=args,
            train_dataset=dataset
        )

        print("🚀 Starting training...")

        trainer.train()

        print("💾 Saving model...")

        trainer.save_model(OUTPUT_DIR)

        self.tokenizer.save_pretrained(OUTPUT_DIR)

        print("✅ TRAINING COMPLETE")

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    trainer = EmotionTrainer()

    trainer.train()