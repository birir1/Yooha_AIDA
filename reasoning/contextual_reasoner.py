# ============================================================
# contextual_reasoner.py
# Core reasoning fusion layer for Memory-Augmented AI Assistant
# Combines memory, emotion, retrieval, and safety signals
# ============================================================

from typing import Dict, List, Any, Optional
import numpy as np


# ============================================================
# CONTEXTUAL REASONER
# ============================================================

class ContextualReasoner:

    def __init__(self):

        print("🚀 Initializing Contextual Reasoner...")

        # adaptive weighting schema (not hardcoded rules, but soft priors)
        self.weights = {
            "memory": 0.35,
            "emotion": 0.20,
            "retrieval": 0.25,
            "safety": 0.20
        }

        print("✅ Contextual Reasoner Ready.")

    # ========================================================
    # MAIN FUSION FUNCTION
    # ========================================================

    def reason(
        self,
        user_message: str,
        memory_context: Dict[str, Any],
        emotion: Dict[str, Any],
        retrieval: List[Dict[str, Any]],
        safety: Dict[str, Any]
    ) -> Dict[str, Any]:

        """
        Produces a unified reasoning state for downstream LLM generation.
        """

        # ====================================================
        # STEP 1: NORMALIZE INPUT SIGNALS
        # ====================================================

        memory_score = self._extract_memory_score(memory_context)

        emotion_score = self._extract_emotion_score(emotion)

        retrieval_score = self._extract_retrieval_score(retrieval)

        safety_score = self._extract_safety_score(safety)

        # ====================================================
        # STEP 2: FUSION ENGINE
        # ====================================================

        fused_score = self._fuse(
            memory_score,
            emotion_score,
            retrieval_score,
            safety_score
        )

        # ====================================================
        # STEP 3: DECISION VECTOR
        # ====================================================

        decision = self._generate_decision_vector(
            fused_score,
            safety_score
        )

        # ====================================================
        # STEP 4: CONTEXTUAL SUMMARY
        # ====================================================

        summary = self._generate_summary(
            user_message,
            memory_context,
            emotion,
            retrieval,
            safety
        )

        return {
            "fused_score": round(fused_score, 4),
            "memory_score": round(memory_score, 4),
            "emotion_score": round(emotion_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "safety_score": round(safety_score, 4),
            "decision_vector": decision,
            "summary": summary
        }

    # ========================================================
    # MEMORY SCORE EXTRACTION
    # ========================================================

    def _extract_memory_score(self, memory_context: Dict[str, Any]) -> float:

        try:

            memories = memory_context.get(
                "context_window", {}
            ).get("memories", {}).get("memories", [])

            if not memories:
                return 0.5

            scores = [
                m.get("score", 0.5)
                for m in memories
            ]

            return float(np.mean(scores))

        except:

            return 0.5

    # ========================================================
    # EMOTION SCORE EXTRACTION
    # ========================================================

    def _extract_emotion_score(self, emotion: Dict[str, Any]) -> float:

        try:

            return float(emotion.get("confidence", 0.5))

        except:

            return 0.5

    # ========================================================
    # RETRIEVAL SCORE EXTRACTION
    # ========================================================

    def _extract_retrieval_score(self, retrieval: List[Dict[str, Any]]) -> float:

        if not retrieval:
            return 0.5

        try:

            scores = [
                r.get("score", 0.5)
                for r in retrieval
            ]

            return float(np.mean(scores))

        except:

            return 0.5

    # ========================================================
    # SAFETY SCORE EXTRACTION
    # ========================================================

    def _extract_safety_score(self, safety: Dict[str, Any]) -> float:

        try:

            # hallucination risk inverted into safety score
            risk = float(safety.get("hallucination_risk", 0.5))

            return float(1.0 - risk)

        except:

            return 0.5

    # ========================================================
    # FUSION ENGINE
    # ========================================================

    def _fuse(
        self,
        memory_score: float,
        emotion_score: float,
        retrieval_score: float,
        safety_score: float
    ) -> float:

        fused = (
            memory_score * self.weights["memory"] +
            emotion_score * self.weights["emotion"] +
            retrieval_score * self.weights["retrieval"] +
            safety_score * self.weights["safety"]
        )

        return float(np.clip(fused, 0.0, 1.0))

    # ========================================================
    # DECISION VECTOR GENERATION
    # ========================================================

    def _generate_decision_vector(
        self,
        fused_score: float,
        safety_score: float
    ) -> Dict[str, Any]:

        decision = {
            "respond": True,
            "confidence_level": "medium",
            "needs_caution": False
        }

        if safety_score < 0.4:
            decision["needs_caution"] = True

        if fused_score > 0.75:
            decision["confidence_level"] = "high"

        elif fused_score < 0.4:
            decision["confidence_level"] = "low"

        return decision

    # ========================================================
    # CONTEXT SUMMARY GENERATION
    # ========================================================

    def _generate_summary(
        self,
        user_message: str,
        memory_context: Dict[str, Any],
        emotion: Dict[str, Any],
        retrieval: List[Dict[str, Any]],
        safety: Dict[str, Any]
    ) -> str:

        emotion_label = emotion.get("emotion", "neutral")

        memory_hint = "no strong memory signals"

        try:

            memories = memory_context.get(
                "context_window", {}
            ).get("memories", {}).get("memories", [])

            if memories:

                memory_hint = " | ".join(
                    m.get("memory", "") or m.get("text", "")
                    for m in memories[:2]
                )

        except:
            pass

        return (
            f"User intent: {user_message[:60]} | "
            f"Emotion: {emotion_label} | "
            f"Memory: {memory_hint}"
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    reasoner = ContextualReasoner()

    sample = reasoner.reason(

        user_message="I want to learn AI",

        memory_context={
            "context_window": {
                "memories": {
                    "memories": [
                        {"memory": "User likes AI", "score": 0.9},
                        {"memory": "User studies ML", "score": 0.8}
                    ]
                }
            }
        },

        emotion={"emotion": "joy", "confidence": 0.85},

        retrieval=[
            {"score": 0.8},
            {"score": 0.7}
        ],

        safety={"hallucination_risk": 0.2}
    )

    print("\n=== REASONING OUTPUT ===")
    print(sample)