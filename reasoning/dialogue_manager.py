# ============================================================
# dialogue_manager.py
# Central Cognitive Orchestration Layer (UPGRADED)
# Memory + Emotion + Reasoning → LLM Decision Engine
# ============================================================

from typing import Dict, List, Any, Optional
from datetime import datetime


# ============================================================
# DIALOGUE MANAGER (COGNITIVE CONTROLLER)
# ============================================================

class DialogueManager:

    def __init__(self):

        print("🚀 Initializing Dialogue Manager (Cognitive Engine)...")

        self.conversation_state = {}

        print("✅ Dialogue Manager Ready.")

    # ========================================================
    # MAIN ORCHESTRATION ENTRY
    # ========================================================

    def build_dialogue_payload(
        self,
        user_message: str,
        context: Dict[str, Any],
        emotion: Dict[str, Any],
        tone: Dict[str, Any],
        reasoning: Dict[str, Any],
        memories: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:

        memories = memories or []

        # ====================================================
        # STEP 1: ANALYZE INPUT SIGNALS
        # ====================================================

        emotion_state = self._extract_emotion(emotion)
        memory_block = self._extract_memories(memories)
        tone_profile = self._extract_tone(tone)
        reasoning_state = self._extract_reasoning(reasoning)

        # ====================================================
        # STEP 2: DECISION LAYER (IMPORTANT ADDITION)
        # ====================================================

        decision_flags = self._compute_decision_flags(
            emotion_state,
            memory_block,
            reasoning_state
        )

        # ====================================================
        # STEP 3: SYSTEM PROMPT CONSTRUCTION
        # ====================================================

        system_prompt = self._build_system_prompt(
            context=context,
            emotion=emotion_state,
            tone=tone_profile,
            reasoning=reasoning_state,
            decisions=decision_flags
        )

        # ====================================================
        # STEP 4: FINAL PAYLOAD
        # ====================================================

        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_prompt": system_prompt,
            "user_message": user_message,
            "context_summary": context.get("summary", ""),
            "emotion": emotion_state,
            "tone": tone_profile,
            "reasoning": reasoning_state,
            "memory_context": memory_block,
            "decisions": decision_flags,
            "metadata": {
                "memory_count": len(memories),
                "emotion_detected": bool(emotion),
                "reasoning_active": bool(reasoning)
            }
        }

        return payload

    # ========================================================
    # DECISION ENGINE (NEW CORE ADDITION)
    # ========================================================

    def _compute_decision_flags(
        self,
        emotion: str,
        memories: List[str],
        reasoning: Dict[str, Any]
    ) -> Dict[str, Any]:

        flags = {
            "use_memory": len(memories) > 0,
            "use_empathy_boost": emotion in ["sadness", "fear", "anger"],
            "use_high_reasoning": bool(reasoning),
            "be_concise": emotion in ["neutral", "sadness"],
            "increase_warmth": emotion in ["joy", "surprise"],
            "risk_of_confusion": False
        }

        # Simple heuristic
        if len(memories) > 8:
            flags["risk_of_confusion"] = True

        return flags

    # ========================================================
    # SYSTEM PROMPT BUILDER (UPGRADED CONTROL AWARE)
    # ========================================================

    def _build_system_prompt(
        self,
        context: Dict[str, Any],
        emotion: str,
        tone: Dict[str, Any],
        reasoning: Dict[str, Any],
        decisions: Dict[str, Any]
    ) -> str:

        return f"""
You are a cognitive memory-augmented empathetic AI assistant.

You operate using:
- long-term memory retrieval
- emotional adaptation
- reasoning-based decision making
- structured conversation control

----------------------------
CONTEXT SUMMARY
----------------------------
{context.get("summary", "")}

----------------------------
EMOTION STATE
----------------------------
{emotion}

----------------------------
REASONING STATE
----------------------------
{reasoning.get("summary", "")}

----------------------------
DECISION FLAGS
----------------------------
{decisions}

----------------------------
BEHAVIOR RULES
----------------------------
- If use_memory=true → integrate memories naturally
- If use_empathy_boost=true → prioritize empathy
- If increase_warmth=true → be warmer and supportive
- If be_concise=true → respond briefly
- Never hallucinate missing facts
- Always stay grounded in context

Respond as a thoughtful, emotionally aware assistant.
""".strip()

    # ========================================================
    # MEMORY EXTRACTION
    # ========================================================

    def _extract_memories(self, memories: List[Dict[str, Any]]) -> List[str]:

        cleaned = []

        for m in memories:

            if isinstance(m, dict):

                text = (
                    m.get("memory")
                    or m.get("text")
                    or str(m)
                )
            else:
                text = str(m)

            if text:
                cleaned.append(text)

        return cleaned

    # ========================================================
    # EMOTION EXTRACTION
    # ========================================================

    def _extract_emotion(self, emotion: Dict[str, Any]) -> str:

        if not emotion:
            return "neutral"

        return emotion.get("emotion", "neutral")

    # ========================================================
    # TONE EXTRACTION
    # ========================================================

    def _extract_tone(self, tone: Dict[str, Any]) -> Dict[str, Any]:

        if not tone:
            return {}

        return tone.get("tone_profile", tone)

    # ========================================================
    # REASONING EXTRACTION
    # ========================================================

    def _extract_reasoning(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:

        if not reasoning:
            return {}

        return reasoning

    # ========================================================
    # STATE TRACKING
    # ========================================================

    def update_state(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str
    ):

        if session_id not in self.conversation_state:

            self.conversation_state[session_id] = []

        self.conversation_state[session_id].append({
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.utcnow().isoformat()
        })

    # ========================================================
    # HISTORY ACCESS
    # ========================================================

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:

        return self.conversation_state.get(session_id, [])