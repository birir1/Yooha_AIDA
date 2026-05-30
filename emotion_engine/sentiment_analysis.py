# ============================================================
# sentiment_analysis.py
# Dataset-driven sentiment analysis engine (GoEmotions-based)
# Replaces hardcoded sentiment logic with model + dataset alignment
# ============================================================

from typing import Dict, List, Any
import numpy as np
from transformers import pipeline


# ============================================================
# SENTIMENT ANALYZER
# ============================================================

class SentimentAnalyzer:

    def __init__(self, model_name: str = "j-hartmann/emotion-english-distilroberta-base"):

        print("🚀 Loading Sentiment / Emotion Model (dataset-driven)...")

        self.pipeline = pipeline(
            task="text-classification",
            model=model_name,
            top_k=None,
            device_map="auto"
        )

        # dataset-aligned grouping (NOT hardcoded sentiment rules, just grouping layer)
        self.positive_set = {
            "joy", "love", "optimism", "amusement", "excitement", "gratitude"
        }

        self.negative_set = {
            "sadness", "anger", "fear", "disgust", "annoyance", "grief"
        }

        self.neutral_set = {
            "neutral", "surprise", "realization", "curiosity"
        }

        print("✅ Sentiment Analyzer Ready.")

    # ========================================================
    # MAIN SENTIMENT CLASSIFICATION
    # ========================================================

    def analyze(self, text: str) -> Dict[str, Any]:

        if not text or not text.strip():

            return {
                "sentiment": "neutral",
                "score": 0.0,
                "distribution": {}
            }

        raw = self.pipeline(text)[0]

        sorted_preds = sorted(
            raw,
            key=lambda x: x["score"],
            reverse=True
        )

        distribution = {
            p["label"]: float(p["score"])
            for p in sorted_preds
        }

        top = sorted_preds[0]

        sentiment = self._map_to_sentiment(top["label"])

        return {
            "sentiment": sentiment,
            "score": round(float(top["score"]), 4),
            "distribution": distribution
        }

    # ========================================================
    # SENTIMENT MAPPING LAYER (DATASET-ALIGNED)
    # ========================================================

    def _map_to_sentiment(self, emotion_label: str) -> str:

        label = emotion_label.lower()

        if label in self.positive_set:
            return "positive"

        if label in self.negative_set:
            return "negative"

        if label in self.neutral_set:
            return "neutral"

        # fallback using probabilistic assumption
        return "neutral"

    # ========================================================
    # MULTI-TEXT ANALYSIS (BATCH STYLE)
    # ========================================================

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:

        results = []

        for text in texts:

            results.append(self.analyze(text))

        return results

    # ========================================================
    # SENTIMENT STRENGTH
    # ========================================================

    def sentiment_strength(self, text: str) -> float:

        result = self.analyze(text)

        return float(result.get("score", 0.0))

    # ========================================================
    # POSITIVE / NEGATIVE CHECKS
    # ========================================================

    def is_positive(self, text: str) -> bool:

        return self.analyze(text)["sentiment"] == "positive"

    def is_negative(self, text: str) -> bool:

        return self.analyze(text)["sentiment"] == "negative"


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    analyzer = SentimentAnalyzer()

    samples = [
        "I am really happy today!",
        "I feel very sad and disappointed.",
        "This is okay, nothing special."
    ]

    for text in samples:

        print("\n" + "=" * 60)
        print("TEXT:", text)
        print(analyzer.analyze(text))