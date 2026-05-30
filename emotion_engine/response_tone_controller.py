# ============================================================
# response_tone_controller.py
# Emotion + Risk Aware Tone Control Engine
# Memory-Augmented AI Assistant
# ============================================================

from typing import Dict, Any, Optional
import numpy as np


# ============================================================
# TONE CONTROLLER
# ============================================================

class ResponseToneController:

    def __init__(self):

        print("🚀 Initializing Response Tone Controller...")

        # base tone schema (data-driven defaults, not hard rules)
        self.base_tone = {
            "empathy": 0.5,
            "formality": 0.5,
            "verbosity": 0.5,
            "confidence": 0.5,
            "warmth": 0.5,
            "caution": 0.5
        }

        print("✅ Tone Controller Ready.")

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def build_tone_profile(
        self,
        emotion: Dict[str, Any],
        context: Dict[str, Any],
        hallucination_report: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None
    ) -> Dict[str, Any]:

        """
        Produces a dynamic tone profile for LLM prompting.
        Fully data-driven (no hardcoded rule triggers).
        """

        hallucination_report = hallucination_report or {}

        # ====================================================
        # STEP 1: EXTRACT SIGNALS
        # ====================================================

        emotion_vector = self._extract_emotion(emotion)

        context_strength = self._extract_context_strength(context)

        risk = self._extract_risk(hallucination_report)

        # ====================================================
        # STEP 2: AGGREGATE SIGNALS
        # ====================================================

        tone = self._aggregate_tone(
            emotion_vector=emotion_vector,
            context_strength=context_strength,
            risk=risk,
            intent=intent
        )

        # ====================================================
        # STEP 3: NORMALIZE OUTPUT
        # ====================================================

        tone = self._normalize(tone)

        return {
            "tone_profile": tone,
            "emotion_vector": emotion_vector,
            "context_strength": context_strength,
            "risk_level": risk
        }

    # ========================================================
    # EMOTION EXTRACTION
    # ========================================================

    def _extract_emotion(
        self,
        emotion: Dict[str, Any]
    ) -> Dict[str, float]:

        if not emotion:

            return {"neutral": 1.0}

        label = emotion.get("emotion", "neutral")

        confidence = float(emotion.get("confidence", 0.0))

        return {label: confidence}

    # ========================================================
    # CONTEXT STRENGTH
    # ========================================================

    def _extract_context_strength(
        self,
        context: Dict[str, Any]
    ) -> float:

        try:

            return float(
                context.get(
                    "context_strength",
                    0.5
                )
            )

        except:

            return 0.5

    # ========================================================
    # HALLUCINATION / RISK EXTRACTION
    # ========================================================

    def _extract_risk(
        self,
        report: Dict[str, Any]
    ) -> float:

        try:

            return float(
                report.get(
                    "hallucination_risk",
                    0.5
                )
            )

        except:

            return 0.5

    # ========================================================
    # TONE AGGREGATION ENGINE
    # ========================================================

    def _aggregate_tone(
        self,
        emotion_vector: Dict[str, float],
        context_strength: float,
        risk: float,
        intent: Optional[str]
    ) -> Dict[str, float]:

        tone = dict(self.base_tone)

        # ====================================================
        # EMOTION INFLUENCE (SOFT MAPPING, NOT RULES)
        # ====================================================

        emotion_name = list(emotion_vector.keys())[0]
        emotion_value = list(emotion_vector.values())[0]

        # emotional weight distribution (continuous scaling)
        tone["empathy"] += emotion_value * 0.4
        tone["warmth"] += emotion_value * 0.3

        # sadness/anxiety-like states implicitly reduce confidence
        tone["confidence"] -= emotion_value * 0.2

        # ====================================================
        # CONTEXT INFLUENCE
        # ====================================================

        tone["verbosity"] += context_strength * 0.3
        tone["confidence"] += context_strength * 0.2

        # ====================================================
        # RISK INFLUENCE (HALLUCINATION SAFETY LAYER)
        # ====================================================

        tone["caution"] += risk * 0.6
        tone["confidence"] -= risk * 0.4

        # higher risk → more formal, less speculative
        tone["formality"] += risk * 0.3

        # ====================================================
        # INTENT ADJUSTMENT (LIGHTWEIGHT, NOT HARD RULES)
        # ====================================================

        if intent:

            intent = intent.lower()

            if intent == "technical_question":

                tone["formality"] += 0.2
                tone["verbosity"] += 0.1

            elif intent == "emotional_support":

                tone["empathy"] += 0.3
                tone["warmth"] += 0.3
                tone["confidence"] -= 0.2

            elif intent == "casual_conversation":

                tone["warmth"] += 0.2
                tone["formality"] -= 0.2

        return tone

    # ========================================================
    # NORMALIZATION
    # ========================================================

    def _normalize(
        self,
        tone: Dict[str, float]
    ) -> Dict[str, float]:

        normalized = {}

        for k, v in tone.items():

            normalized[k] = float(
                np.clip(v, 0.0, 1.0)
            )

        return normalized

    # ========================================================
    # TONE → PROMPT INSTRUCTIONS
    # ========================================================

    def to_prompt_instructions(
        self,
        tone_profile: Dict[str, float]
    ) -> str:

        """
        Converts tone vector into LLM prompt instructions.
        """

        return f"""
TONE CONTROL SETTINGS:

- Empathy Level: {tone_profile.get('empathy', 0.5)}
- Warmth Level: {tone_profile.get('warmth', 0.5)}
- Formality Level: {tone_profile.get('formality', 0.5)}
- Verbosity Level: {tone_profile.get('verbosity', 0.5)}
- Confidence Level: {tone_profile.get('confidence', 0.5)}
- Caution Level: {tone_profile.get('caution', 0.5)}

INSTRUCTIONS:
- Adjust response style according to the above tone profile
- Higher caution → be more careful and less speculative
- Higher empathy → be more emotionally supportive
- Higher verbosity → provide more detailed explanations
- Lower confidence → avoid over-assertive claims
""".strip()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    controller = ResponseToneController()

    sample_emotion = {
        "emotion": "sadness",
        "confidence": 0.9
    }

    sample_context = {
        "context_strength": 0.75
    }

    sample_risk = {
        "hallucination_risk": 0.3
    }

    tone = controller.build_tone_profile(

        emotion=sample_emotion,
        context=sample_context,
        hallucination_report=sample_risk,
        intent="emotional_support"
    )

    print("\n=== TONE PROFILE ===")
    print(tone)

    print("\n=== PROMPT INSTRUCTIONS ===")
    print(
        controller.to_prompt_instructions(
            tone["tone_profile"]
        )
    )