# ============================================================
# hallucination_checker.py
# Hallucination Detection + Context Grounding Validator
# Memory-Augmented AI Safety Layer
# ============================================================

from typing import Dict, List, Any, Optional
import re
import numpy as np


# ============================================================
# HALLUCINATION CHECKER
# ============================================================

class HallucinationChecker:

    def __init__(self):

        print("🚀 Initializing Hallucination Checker...")

        # lightweight heuristic signals (NO hardcoded facts, only structure)
        self.uncertainty_markers = [
            "maybe", "probably", "i think", "i guess",
            "not sure", "could be", "possibly"
        ]

        self.overconfident_markers = [
            "definitely", "always", "never", "guaranteed",
            "100%", "no doubt"
        ]

        print("✅ Hallucination Checker Ready.")

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def analyze(
        self,
        response: str,
        context: Dict[str, Any],
        memories: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:

        """
        Returns hallucination risk + grounding score
        """

        if not response:

            return {
                "hallucination_risk": 1.0,
                "grounding_score": 0.0,
                "flags": ["empty_response"]
            }

        memories = memories or []

        # ====================================================
        # STEP 1: MEMORY GROUNDING CHECK
        # ====================================================

        memory_score = self._check_memory_grounding(
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
        # STEP 3: LINGUISTIC UNCERTAINTY ANALYSIS
        # ====================================================

        language_score, lang_flags = self._analyze_language(
            response
        )

        # ====================================================
        # STEP 4: CONSISTENCY CHECK
        # ====================================================

        consistency_score = self._check_consistency(
            response
        )

        # ====================================================
        # FINAL SCORE COMPUTATION (DATA-DRIVEN WEIGHTING)
        # ====================================================

        grounding_score = float(np.mean([
            memory_score,
            context_score,
            consistency_score
        ]))

        hallucination_risk = float(
            1.0 - grounding_score
        )

        # adjust with language uncertainty
        hallucination_risk = float(
            np.clip(
                (hallucination_risk + (1.0 - language_score)) / 2,
                0.0,
                1.0
            )
        )

        # ====================================================
        # FLAGS
        # ====================================================

        flags = []

        if hallucination_risk > 0.7:
            flags.append("high_hallucination_risk")

        if memory_score < 0.4:
            flags.append("low_memory_grounding")

        if context_score < 0.4:
            flags.append("weak_context_alignment")

        if consistency_score < 0.4:
            flags.append("inconsistent_response")

        flags.extend(lang_flags)

        return {

            "hallucination_risk": round(hallucination_risk, 4),

            "grounding_score": round(grounding_score, 4),

            "memory_score": round(memory_score, 4),

            "context_score": round(context_score, 4),

            "language_score": round(language_score, 4),

            "flags": list(set(flags))
        }

    # ========================================================
    # MEMORY GROUNDING CHECK
    # ========================================================

    def _check_memory_grounding(
        self,
        response: str,
        memories: List[Dict]
    ) -> float:

        if not memories:
            return 0.5  # neutral uncertainty

        response_lower = response.lower()

        matches = 0

        for m in memories:

            memory_text = str(
                m.get("memory", "")
            ).lower()

            if not memory_text:
                continue

            # simple semantic overlap proxy (no hard rules)
            overlap = len(
                set(response_lower.split())
                & set(memory_text.split())
            )

            if overlap > 0:
                matches += 1

        return float(
            min(matches / len(memories), 1.0)
        )

    # ========================================================
    # CONTEXT ALIGNMENT CHECK
    # ========================================================

    def _check_context_alignment(
        self,
        response: str,
        context: Dict
    ) -> float:

        if not context:
            return 0.5

        response_tokens = set(
            response.lower().split()
        )

        alignment_hits = 0
        total_checks = 0

        # check memory alignment
        try:

            memories = context.get(
                "context_window", {}
            ).get("memories", {}).get("memories", [])

            for m in memories:

                text = m.get("text", "").lower()

                if text:

                    total_checks += 1

                    if len(
                        response_tokens
                        & set(text.split())
                    ) > 0:

                        alignment_hits += 1

        except:
            pass

        if total_checks == 0:
            return 0.5

        return float(
            alignment_hits / total_checks
        )

    # ========================================================
    # LANGUAGE ANALYSIS
    # ========================================================

    def _analyze_language(
        self,
        response: str
    ) -> (float, List[str]):

        text = response.lower()

        uncertainty_count = sum(
            1 for w in self.uncertainty_markers
            if w in text
        )

        overconfidence_count = sum(
            1 for w in self.overconfident_markers
            if w in text
        )

        flags = []

        if overconfidence_count > 0:
            flags.append("overconfident_language")

        if uncertainty_count > 0:
            flags.append("uncertain_language")

        # normalize score
        score = 1.0 - min(
            (uncertainty_count + overconfidence_count) * 0.1,
            1.0
        )

        return float(score), flags

    # ========================================================
    # CONSISTENCY CHECK
    # ========================================================

    def _check_consistency(
        self,
        response: str
    ) -> float:

        sentences = re.split(
            r'[.!?]',
            response
        )

        sentences = [
            s.strip()
            for s in sentences
            if s.strip()
        ]

        if len(sentences) < 2:
            return 0.7

        # simple repetition detection
        unique = len(set(sentences))

        return float(unique / len(sentences))


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    checker = HallucinationChecker()

    sample_response = (
        "User likes AI and cybersecurity. "
        "They are learning machine learning."
    )

    sample_context = {
        "context_window": {
            "memories": {
                "memories": [
                    {"text": "User likes AI"},
                    {"text": "User studies cybersecurity"}
                ]
            }
        }
    }

    result = checker.analyze(
        response=sample_response,
        context=sample_context,
        memories=[
            {"memory": "User likes AI"},
            {"memory": "User studies cybersecurity"}
        ]
    )

    print("\n=== HALLUCINATION RESULT ===")
    print(result)