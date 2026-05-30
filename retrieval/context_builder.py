# ============================================================
# context_builder.py
# Dataset-Driven Context Fusion Engine (No Hardcoding Core)
# ============================================================

from typing import Dict, List, Any, Optional
import numpy as np


# ============================================================
# CONTEXT BUILDER
# ============================================================

class ContextBuilder:

    def __init__(self, config: Optional[Dict] = None):

        print("🚀 Initializing Context Builder (Dataset-Driven)...")

        self.config = config or {}

        # default weighting (can later be learned from datasets)
        self.default_weights = {
            "memory": 0.45,
            "emotion": 0.20,
            "recency": 0.20,
            "semantic": 0.15
        }

        print("✅ Context Builder Ready.")

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def build_context(
        self,
        user_message: str,
        memories: List[Dict],
        emotion: Dict[str, Any],
        conversation_history: List[Dict],
        dataset_signals: Optional[Dict] = None
    ) -> Dict[str, Any]:

        """
        Builds a unified context representation for the LLM.
        Fully data-driven fusion (no rule-based logic dependency).
        """

        dataset_signals = dataset_signals or {}

        # ====================================================
        # STEP 1: MEMORY SCORING
        # ====================================================

        memory_block = self._process_memories(memories)

        # ====================================================
        # STEP 2: EMOTION VECTOR NORMALIZATION
        # ====================================================

        emotion_block = self._process_emotion(emotion)

        # ====================================================
        # STEP 3: HISTORY PROCESSING
        # ====================================================

        history_block = self._process_history(conversation_history)

        # ====================================================
        # STEP 4: DATASET ALIGNMENT SIGNALS
        # ====================================================

        dataset_block = self._process_dataset_signals(dataset_signals)

        # ====================================================
        # STEP 5: CONTEXT FUSION
        # ====================================================

        fused_context = self._fuse_context(
            user_message=user_message,
            memory_block=memory_block,
            emotion_block=emotion_block,
            history_block=history_block,
            dataset_block=dataset_block
        )

        return fused_context

    # ========================================================
    # MEMORY PROCESSING
    # ========================================================

    def _process_memories(self, memories: List[Dict]) -> Dict[str, Any]:

        if not memories:

            return {
                "memories": [],
                "memory_score": 0.0
            }

        processed = []

        scores = []

        for m in memories:

            text = m.get("memory", "")

            score = m.get("score", 0.5)

            processed.append({
                "text": text,
                "score": score,
                "source": m.get("source", "unknown"),
                "metadata": m.get("metadata", {})
            })

            scores.append(score)

        return {

            "memories": processed,

            "memory_score": float(
                np.mean(scores)
                if scores else 0.0
            )
        }

    # ========================================================
    # EMOTION PROCESSING (DATA-DRIVEN NORMALIZATION ONLY)
    # ========================================================

    def _process_emotion(self, emotion: Dict[str, Any]) -> Dict[str, Any]:

        if not emotion:

            return {
                "emotion": "neutral",
                "confidence": 0.0,
                "vector": {}
            }

        emotion_label = emotion.get("emotion", "neutral")

        confidence = float(emotion.get("confidence", 0.0))

        # convert to soft vector (no hard rules, just representation)
        emotion_vector = {
            emotion_label: confidence
        }

        return {

            "emotion": emotion_label,

            "confidence": confidence,

            "vector": emotion_vector
        }

    # ========================================================
    # HISTORY PROCESSING
    # ========================================================

    def _process_history(
        self,
        history: List[Dict]
    ) -> Dict[str, Any]:

        if not history:

            return {
                "history": [],
                "recency_score": 0.0
            }

        processed = []

        for h in history[-10:]:

            processed.append({
                "user": h.get("user", ""),
                "assistant": h.get("assistant", "")
            })

        # simple recency signal (dataset-driven systems can replace later)
        recency_score = min(len(processed) / 10.0, 1.0)

        return {

            "history": processed,

            "recency_score": recency_score
        }

    # ========================================================
    # DATASET SIGNAL PROCESSING (KEY PART)
    # ========================================================

    def _process_dataset_signals(
        self,
        signals: Dict
    ) -> Dict[str, Any]:

        """
        This is where dataset learning plugs in:
        - GoEmotions
        - PersonaChat
        - memory_training_dataset
        - synthetic_empathy_dataset
        """

        if not signals:

            return {
                "alignment_score": 0.0,
                "signals": {}
            }

        # no hardcoding weights; just pass-through aggregation
        alignment_values = []

        for k, v in signals.items():

            try:
                alignment_values.append(float(v))
            except:
                continue

        return {

            "alignment_score": float(
                np.mean(alignment_values)
                if alignment_values else 0.0
            ),

            "signals": signals
        }

    # ========================================================
    # CONTEXT FUSION CORE
    # ========================================================

    def _fuse_context(
        self,
        user_message: str,
        memory_block: Dict,
        emotion_block: Dict,
        history_block: Dict,
        dataset_block: Dict
    ) -> Dict[str, Any]:

        """
        No rule-based logic here.
        Only structured fusion of signals.
        """

        context_window = {

            "user_message": user_message,

            "memories": memory_block,

            "emotion": emotion_block,

            "history": history_block,

            "dataset_signals": dataset_block
        }

        # global context strength (data-driven aggregation)
        context_strength = float(np.mean([

            memory_block.get("memory_score", 0.0),

            emotion_block.get("confidence", 0.0),

            history_block.get("recency_score", 0.0),

            dataset_block.get("alignment_score", 0.0)

        ]))

        return {

            "context_window": context_window,

            "context_strength": round(context_strength, 4),

            "summary": self._build_summary(context_window)
        }

    # ========================================================
    # CONTEXT SUMMARY (LLM-FRIENDLY OUTPUT)
    # ========================================================

    def _build_summary(self, context: Dict) -> str:

        memories = context["memories"]["memories"]

        emotion = context["emotion"]["emotion"]

        history = context["history"]["history"]

        summary_parts = []

        # MEMORY SUMMARY
        if memories:

            top_memory = memories[0]["text"]

            summary_parts.append(
                f"Relevant memory: {top_memory}"
            )

        # EMOTION SUMMARY
        summary_parts.append(
            f"User emotion: {emotion}"
        )

        # HISTORY SUMMARY
        if history:

            last_turn = history[-1]

            summary_parts.append(
                f"Recent interaction exists"
            )

        return " | ".join(summary_parts)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    builder = ContextBuilder()

    sample_memories = [
        {"memory": "User likes AI", "score": 0.9},
        {"memory": "User studies cybersecurity", "score": 0.8}
    ]

    sample_emotion = {
        "emotion": "joy",
        "confidence": 0.87
    }

    sample_history = [
        {"user": "hi", "assistant": "hello"},
        {"user": "tell me about AI", "assistant": "AI is..."}
    ]

    result = builder.build_context(

        user_message="I want to learn AI",

        memories=sample_memories,

        emotion=sample_emotion,

        conversation_history=sample_history,

        dataset_signals={"goemotions": 0.8, "persona": 0.6}
    )

    print("\n=== CONTEXT RESULT ===")
    print(result)