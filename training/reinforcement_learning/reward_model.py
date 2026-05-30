# ============================================================
# reward_model.py
# Reward Model for Reinforcement Learning in AI Assistant
# Estimates response quality (empathy, relevance, clarity, safety)
# ============================================================

from typing import Dict, Any
import math


# ============================================================
# REWARD MODEL
# ============================================================

class RewardModel:

    def __init__(self):

        print("🚀 Initializing Reward Model...")

        # simple keyword-based heuristics (can be replaced with neural model later)
        self.empathy_keywords = [
            "sorry", "understand", "feel", "help", "care", "support"
        ]

        self.clarity_keywords = [
            "because", "therefore", "for example", "step", "first", "second"
        ]

        self.relevance_keywords = [
            "you", "your", "memory", "context", "remember", "based on"
        ]

        print("✅ Reward Model Ready.")

    # ========================================================
    # SCORE COMPONENTS
    # ========================================================

    def _score_empathy(self, text: str) -> float:

        text = text.lower()

        hits = sum(1 for k in self.empathy_keywords if k in text)

        return min(hits / 3.0, 1.0)

    def _score_clarity(self, text: str) -> float:

        text = text.lower()

        hits = sum(1 for k in self.clarity_keywords if k in text)

        return min(hits / 3.0, 1.0)

    def _score_relevance(self, text: str) -> float:

        text = text.lower()

        hits = sum(1 for k in self.relevance_keywords if k in text)

        return min(hits / 3.0, 1.0)

    def _score_safety(self, text: str) -> float:

        # simple safety heuristic (placeholder)
        unsafe_keywords = [
            "kill", "hack", "exploit", "attack", "illegal"
        ]

        hits = sum(1 for k in unsafe_keywords if k in text)

        return 1.0 - min(hits / 3.0, 1.0)

    # ========================================================
    # MAIN REWARD FUNCTION
    # ========================================================

    def compute_reward(
        self,
        user_message: str,
        assistant_response: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, float]:

        if context is None:
            context = {}

        text = assistant_response.lower()

        empathy = self._score_empathy(text)
        clarity = self._score_clarity(text)
        relevance = self._score_relevance(text)
        safety = self._score_safety(text)

        # weighted reward
        total_reward = (
            0.35 * empathy +
            0.25 * clarity +
            0.25 * relevance +
            0.15 * safety
        )

        return {
            "empathy": round(empathy, 4),
            "clarity": round(clarity, 4),
            "relevance": round(relevance, 4),
            "safety": round(safety, 4),
            "reward": round(total_reward, 4)
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    model = RewardModel()

    result = model.compute_reward(
        user_message="I feel sad",
        assistant_response="I understand how you feel. I'm here to help you."
    )

    print("\n=== REWARD OUTPUT ===")
    print(result)