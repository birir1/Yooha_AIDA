# ============================================================
# emotion_memory_mapper.py
# Maps emotional signals to memory importance + storage strategy
# Memory-Augmented AI Assistant
# ============================================================

from typing import Dict, Any, Optional
import numpy as np


# ============================================================
# EMOTION → MEMORY MAPPER
# ============================================================

class EmotionMemoryMapper:

    def __init__(self):

        print("🚀 Initializing Emotion Memory Mapper...")

        # dynamic weighting schema (not hard rules, learned-style scaling)
        self.base_weights = {
            "joy": 0.6,
            "sadness": 0.8,
            "anger": 0.75,
            "fear": 0.85,
            "surprise": 0.5,
            "neutral": 0.4,
            "disgust": 0.7
        }

        print("✅ Emotion Memory Mapper Ready.")

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def map_to_memory_priority(
        self,
        emotion: Dict[str, Any],
        context_strength: float = 0.5,
        user_message: Optional[str] = None
    ) -> Dict[str, Any]:

        """
        Converts emotion signals into memory importance scores
        and storage strategy signals.
        """

        label, confidence = self._extract_emotion(emotion)

        base_weight = self.base_weights.get(label, 0.5)

        # ====================================================
        # DYNAMIC IMPORTANCE SCORING
        # ====================================================

        importance = self._compute_importance(
            label=label,
            confidence=confidence,
            base_weight=base_weight,
            context_strength=context_strength,
            text=user_message or ""
        )

        # ====================================================
        # MEMORY STRATEGY DECISION
        # ====================================================

        strategy = self._decide_storage_strategy(
            importance=importance,
            label=label,
            confidence=confidence
        )

        return {
            "emotion": label,
            "confidence": confidence,
            "importance_score": round(importance, 4),
            "storage_strategy": strategy
        }

    # ========================================================
    # EMOTION EXTRACTION
    # ========================================================

    def _extract_emotion(
        self,
        emotion: Dict[str, Any]
    ):

        if not emotion:

            return "neutral", 0.0

        return (
            emotion.get("emotion", "neutral"),
            float(emotion.get("confidence", 0.0))
        )

    # ========================================================
    # IMPORTANCE SCORING ENGINE
    # ========================================================

    def _compute_importance(
        self,
        label: str,
        confidence: float,
        base_weight: float,
        context_strength: float,
        text: str
    ) -> float:

        score = base_weight * confidence

        # context reinforcement
        score += context_strength * 0.2

        # keyword reinforcement (soft signals, not hard rules)
        emotional_keywords = [
            "important", "remember", "never forget",
            "love", "hate", "goal", "dream",
            "career", "family", "future"
        ]

        text_lower = text.lower()

        keyword_hits = sum(
            1 for k in emotional_keywords if k in text_lower
        )

        score += keyword_hits * 0.05

        # emotional amplification for strong affect states
        if label in ["sadness", "fear", "anger"]:
            score += 0.1 * confidence

        return float(np.clip(score, 0.0, 1.0))

    # ========================================================
    # STORAGE STRATEGY DECISION
    # ========================================================

    def _decide_storage_strategy(
        self,
        importance: float,
        label: str,
        confidence: float
    ) -> Dict[str, Any]:

        strategy = {
            "store": True,
            "memory_type": "general",
            "persistence": "short_term"
        }

        # high importance → long-term memory
        if importance > 0.75:

            strategy["memory_type"] = "episodic"
            strategy["persistence"] = "long_term"

        # medium importance → semantic memory
        elif importance > 0.5:

            strategy["memory_type"] = "semantic"
            strategy["persistence"] = "mid_term"

        # emotional prioritization overrides
        if label in ["fear", "sadness"] and confidence > 0.7:

            strategy["memory_type"] = "episodic"
            strategy["persistence"] = "long_term"

        # neutral low importance → may not store
        if importance < 0.3:

            strategy["store"] = False

        return strategy


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    mapper = EmotionMemoryMapper()

    sample_emotion = {
        "emotion": "sadness",
        "confidence": 0.9
    }

    result = mapper.map_to_memory_priority(
        emotion=sample_emotion,
        context_strength=0.8,
        user_message="I will never forget this moment, it is very important"
    )

    print("\n=== MEMORY MAPPING RESULT ===")
    print(result)