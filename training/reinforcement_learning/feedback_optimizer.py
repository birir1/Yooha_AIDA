# ============================================================
# feedback_optimizer.py
# Reinforcement Learning Feedback Optimizer
# Improves assistant responses using user feedback signals
# ============================================================

from typing import List, Dict, Any, Optional
import random
import math
from datetime import datetime


# ============================================================
# FEEDBACK OPTIMIZER
# ============================================================

class FeedbackOptimizer:

    def __init__(self):

        print("🚀 Initializing Feedback Optimizer (RL Core)...")

        # simple in-memory reward log
        self.feedback_buffer: List[Dict[str, Any]] = []

        # running reward statistics
        self.reward_stats = {
            "total": 0,
            "positive": 0,
            "negative": 0
        }

        print("✅ Feedback Optimizer Ready.")

    # ========================================================
    # ADD FEEDBACK
    # ========================================================

    def add_feedback(
        self,
        user_message: str,
        assistant_response: str,
        reward: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:

        if metadata is None:
            metadata = {}

        record = {
            "user_message": user_message,
            "assistant_response": assistant_response,
            "reward": float(reward),
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata
        }

        self.feedback_buffer.append(record)

        # update stats
        self.reward_stats["total"] += 1

        if reward >= 0:
            self.reward_stats["positive"] += 1
        else:
            self.reward_stats["negative"] += 1

    # ========================================================
    # COMPUTE AVERAGE REWARD
    # ========================================================

    def average_reward(self) -> float:

        if not self.feedback_buffer:
            return 0.0

        total_reward = sum(f["reward"] for f in self.feedback_buffer)

        return round(total_reward / len(self.feedback_buffer), 4)

    # ========================================================
    # SAMPLE BEST RESPONSES
    # ========================================================

    def get_best_responses(self, top_k: int = 5) -> List[Dict[str, Any]]:

        sorted_feedback = sorted(
            self.feedback_buffer,
            key=lambda x: x["reward"],
            reverse=True
        )

        return sorted_feedback[:top_k]

    # ========================================================
    # SAMPLE WORST RESPONSES
    # ========================================================

    def get_worst_responses(self, top_k: int = 5) -> List[Dict[str, Any]]:

        sorted_feedback = sorted(
            self.feedback_buffer,
            key=lambda x: x["reward"]
        )

        return sorted_feedback[:top_k]

    # ========================================================
    # REWARD NORMALIZATION
    # ========================================================

    def normalize_rewards(self) -> List[float]:

        if not self.feedback_buffer:
            return []

        rewards = [f["reward"] for f in self.feedback_buffer]

        min_r = min(rewards)
        max_r = max(rewards)

        if max_r == min_r:
            return [0.5 for _ in rewards]

        return [
            (r - min_r) / (max_r - min_r)
            for r in rewards
        ]

    # ========================================================
    # SIMPLE POLICY UPDATE (SIMULATED RL)
    # ========================================================

    def compute_policy_score(self, response_features: Dict[str, float]) -> float:

        """
        Lightweight scoring function that simulates RL policy improvement.
        """

        weights = {
            "relevance": 0.4,
            "empathy": 0.3,
            "clarity": 0.2,
            "memory_alignment": 0.1
        }

        score = 0.0

        for k, w in weights.items():

            score += response_features.get(k, 0.0) * w

        return round(score, 4)

    # ========================================================
    # SIMULATE UPDATE STEP
    # ========================================================

    def update_policy(self) -> Dict[str, Any]:

        """
        Fake RL update step (placeholder for PPO / DPO integration later)
        """

        avg_reward = self.average_reward()

        adjustment_factor = 1.0 + (avg_reward - 0.5) * 0.1

        return {
            "average_reward": avg_reward,
            "adjustment_factor": round(adjustment_factor, 4),
            "samples": len(self.feedback_buffer)
        }

    # ========================================================
    # EXPORT TRAINING DATA
    # ========================================================

    def export_dataset(self) -> List[Dict[str, Any]]:

        return self.feedback_buffer


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    optimizer = FeedbackOptimizer()

    optimizer.add_feedback(
        "I want to learn AI",
        "That's great! AI is a powerful field.",
        reward=0.9
    )

    optimizer.add_feedback(
        "Tell me something random",
        "I don't understand.",
        reward=0.2
    )

    print("\n=== AVG REWARD ===")
    print(optimizer.average_reward())

    print("\n=== BEST RESPONSES ===")
    print(optimizer.get_best_responses())

    print("\n=== POLICY UPDATE ===")
    print(optimizer.update_policy())