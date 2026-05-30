# ============================================================
# emotion_detector.py
# Emotion-Aware Classification Engine (Production Ready)
# ============================================================

from typing import Dict, List, Any, Optional

import torch
from transformers import pipeline


# ============================================================
# EMOTION DETECTOR
# ============================================================

class EmotionDetector:

    def __init__(self):

        print("🚀 Loading emotion detection model...")

        # ====================================================
        # MODEL PIPELINE
        # ====================================================

        self.classifier = pipeline(

            task="text-classification",

            model="j-hartmann/emotion-english-distilroberta-base",

            top_k=None,

            device=0 if torch.cuda.is_available() else -1
        )

        print("✅ Emotion detector loaded.")

        # ====================================================
        # STANDARDIZED EMOTION MAP
        # (we normalize model labels → system labels)
        # ====================================================

        self.emotion_map = {

            "anger": "anger",
            "disgust": "disgust",
            "fear": "fear",
            "joy": "joy",
            "neutral": "neutral",
            "sadness": "sadness",
            "surprise": "surprise"
        }

    # ========================================================
    # MAIN EMOTION DETECTION
    # ========================================================

    def detect_emotion(
        self,
        text: str
    ) -> Dict[str, Any]:

        if not text or not text.strip():

            return {
                "emotion": "neutral",
                "confidence": 0.0
            }

        try:

            predictions = self.classifier(text)[0]

            # sort by confidence
            predictions = sorted(
                predictions,
                key=lambda x: x["score"],
                reverse=True
            )

            top = predictions[0]

            emotion = top["label"].lower()

            emotion = self.emotion_map.get(
                emotion,
                emotion
            )

            return {

                "emotion": emotion,

                "confidence": round(
                    float(top["score"]),
                    4
                )
            }

        except Exception as e:

            print(f"[EmotionDetector ERROR] {e}")

            return {
                "emotion": "neutral",
                "confidence": 0.0
            }

    # ========================================================
    # FULL DISTRIBUTION
    # ========================================================

    def detect_all_emotions(
        self,
        text: str
    ) -> List[Dict[str, Any]]:

        if not text or not text.strip():

            return [{
                "emotion": "neutral",
                "confidence": 1.0
            }]

        try:

            predictions = self.classifier(text)[0]

            predictions = sorted(
                predictions,
                key=lambda x: x["score"],
                reverse=True
            )

            results = []

            for p in predictions:

                emotion = p["label"].lower()

                emotion = self.emotion_map.get(
                    emotion,
                    emotion
                )

                results.append({

                    "emotion": emotion,

                    "confidence": round(
                        float(p["score"]),
                        4
                    )
                })

            return results

        except Exception as e:

            print(f"[EmotionDetector ERROR] {e}")

            return []

    # ========================================================
    # EMOTION SCORE MAP
    # ========================================================

    def emotion_scores(
        self,
        text: str
    ) -> Dict[str, float]:

        all_emotions = self.detect_all_emotions(text)

        return {
            item["emotion"]: item["confidence"]
            for item in all_emotions
        }

    # ========================================================
    # DOMINANT EMOTION
    # ========================================================

    def dominant_emotion(
        self,
        text: str
    ) -> str:

        return self.detect_emotion(text)["emotion"]

    # ========================================================
    # INTENSITY SCORE
    # ========================================================

    def emotional_intensity(
        self,
        text: str
    ) -> float:

        return self.detect_emotion(text)["confidence"]

    # ========================================================
    # NEGATIVE CHECK
    # ========================================================

    def is_negative(
        self,
        text: str
    ) -> bool:

        negative = {"anger", "fear", "sadness", "disgust"}

        return self.dominant_emotion(text) in negative

    # ========================================================
    # POSITIVE CHECK
    # ========================================================

    def is_positive(
        self,
        text: str
    ) -> bool:

        positive = {"joy", "surprise"}

        return self.dominant_emotion(text) in positive


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    detector = EmotionDetector()

    samples = [

        "I am really happy today.",
        "I feel sad and lonely.",
        "I am frustrated with my exams.",
        "This is exciting news!"
    ]

    for text in samples:

        print("\n" + "=" * 60)

        print(f"TEXT: {text}")

        print("\nTOP EMOTION:")
        print(detector.detect_emotion(text))

        print("\nTOP 3 EMOTIONS:")
        for e in detector.detect_all_emotions(text)[:3]:
            print(e)