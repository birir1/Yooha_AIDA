# ============================================================
# verification_module.py
# Response verification + grounding validator
# Ensures outputs are consistent with memory + context + reasoning
# ============================================================

from typing import Dict, List, Any, Optional
import numpy as np
import re


# ============================================================
# VERIFICATION MODULE
# ============================================================

class VerificationModule:

    def __init__(self):

        print("🚀 Initializing Verification Module...")

        self.conflict_keywords = [
            "however", "but", "although", "instead", "actually"
        ]

        print("✅ Verification Module Ready.")

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def verify(
        self,
        user_message: str,
        response: str,
        context: Dict[str, Any],
        memories: Optional[List[Dict[str, Any]]] = None,
        reasoning: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        """
        Produces verification score + contradiction detection
        """

        memories = memories or []

        # ====================================================
        # STEP 1: MEMORY CONSISTENCY CHECK
        # ====================================================

        memory_score, memory_conflicts = self._check_memory_consistency(
            response,
            memories
        )

        # ====================================================
        # STEP 2: CONTEXT ALIGNMENT CHECK
        # ====================================================

        context_score = self._check_context_alignment(
            response,
            context
        )

        # ====================================================
        # STEP 3: CONTRADICTION DETECTION
        # ====================================================

        contradiction_score = self._detect_contradictions(
            response,
            memories
        )

        # ====================================================
        # STEP 4: REASONING ALIGNMENT CHECK
        # ====================================================

        reasoning_score = self._check_reasoning_alignment(
            response,
            reasoning
        )

        # ====================================================
        # FINAL SCORE COMPUTATION
        # ====================================================

        verification_score = float(np.mean([
            memory_score,
            context_score,
            reasoning_score
        ]))

        risk = float(1.0 - verification_score)

        flags = []

        if memory_conflicts:
            flags.append("memory_conflict")

        if contradiction_score > 0.6:
            flags.append("high_contradiction_risk")

        if verification_score < 0.5:
            flags.append("low_verification_confidence")

        return {
            "verification_score": round(verification_score, 4),
            "risk_score": round(risk, 4),
            "memory_score": round(memory_score, 4),
            "context_score": round(context_score, 4),
            "reasoning_score": round(reasoning_score, 4),
            "contradiction_score": round(contradiction_score, 4),
            "flags": flags,
            "memory_conflicts": memory_conflicts
        }

    # ========================================================
    # MEMORY CONSISTENCY CHECK
    # ========================================================

    def _check_memory_consistency(
        self,
        response: str,
        memories: List[Dict[str, Any]]
    ) -> (float, List[str]):

        if not memories:
            return 0.5, []

        response_tokens = set(response.lower().split())

        score = 0.0
        conflicts = []

        for m in memories:

            mem_text = (m.get("memory") or m.get("text") or "").lower()

            if not mem_text:
                continue

            mem_tokens = set(mem_text.split())

            overlap = len(response_tokens & mem_tokens)

            if overlap > 0:
                score += 1
            else:
                conflicts.append(mem_text)

        score = score / len(memories)

        return float(score), conflicts

    # ========================================================
    # CONTEXT ALIGNMENT CHECK
    # ========================================================

    def _check_context_alignment(
        self,
        response: str,
        context: Dict[str, Any]
    ) -> float:

        try:

            ctx_memories = context.get(
                "context_window", {}
            ).get("memories", {}).get("memories", [])

            if not ctx_memories:
                return 0.5

            response_tokens = set(response.lower().split())

            hits = 0

            for m in ctx_memories:

                text = (m.get("memory") or m.get("text") or "").lower()

                if not text:
                    continue

                if len(response_tokens & set(text.split())) > 0:
                    hits += 1

            return float(hits / len(ctx_memories))

        except:

            return 0.5

    # ========================================================
    # CONTRADICTION DETECTION
    # ========================================================

    def _detect_contradictions(
        self,
        response: str,
        memories: List[Dict[str, Any]]
    ) -> float:

        response_lower = response.lower()

        contradiction_score = 0.0

        for m in memories:

            mem_text = (m.get("memory") or m.get("text") or "").lower()

            if not mem_text:
                continue

            # simple heuristic: presence of negation mismatch
            if "not" in response_lower and "not" not in mem_text:
                contradiction_score += 0.2

            if "like" in response_lower and "dislike" in mem_text:
                contradiction_score += 0.3

            if "dislike" in response_lower and "like" in mem_text:
                contradiction_score += 0.3

        return float(min(contradiction_score, 1.0))

    # ========================================================
    # REASONING ALIGNMENT CHECK
    # ========================================================

    def _check_reasoning_alignment(
        self,
        response: str,
        reasoning: Optional[Dict[str, Any]]
    ) -> float:

        if not reasoning:
            return 0.5

        summary = reasoning.get("summary", "").lower()

        if not summary:
            return 0.5

        response_tokens = set(response.lower().split())
        reasoning_tokens = set(summary.split())

        overlap = len(response_tokens & reasoning_tokens)

        return float(min(overlap / (len(reasoning_tokens) + 1e-6), 1.0))


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    verifier = VerificationModule()

    result = verifier.verify(

        user_message="I want to learn AI",

        response="You like AI and machine learning.",

        context={
            "context_window": {
                "memories": {
                    "memories": [
                        {"memory": "User likes AI"},
                        {"memory": "User studies ML"}
                    ]
                }
            }
        },

        memories=[
            {"memory": "User likes AI"},
            {"memory": "User studies ML"}
        ],

        reasoning={"summary": "User is interested in AI learning path"}
    )

    print("\n=== VERIFICATION RESULT ===")
    print(result)