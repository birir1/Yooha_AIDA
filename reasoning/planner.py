# ============================================================
# planner.py
# Multi-step reasoning planner for Memory-Augmented AI Assistant
# Breaks user intent into structured execution steps
# ============================================================

from typing import Dict, List, Any, Optional
import re


# ============================================================
# PLANNER
# ============================================================

class Planner:

    def __init__(self):

        print("🚀 Initializing Reasoning Planner...")

        # soft intent categories (not hard rules, just guidance priors)
        self.intent_patterns = {
            "learning": [
                r"\blearn\b", r"\bstudy\b", r"\bteach\b",
                r"\bunderstand\b", r"\bexplain\b"
            ],
            "task": [
                r"\bdo\b", r"\bmake\b", r"\bbuild\b",
                r"\bcreate\b", r"\bgenerate\b"
            ],
            "analysis": [
                r"\banalyze\b", r"\bcompare\b", r"\bwhy\b",
                r"\bhow\b"
            ],
            "memory_query": [
                r"\bremember\b", r"\brecall\b", r"\bwhat did i\b"
            ]
        }

        print("✅ Planner Ready.")

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def create_plan(
        self,
        user_message: str,
        context: Dict[str, Any],
        emotion: Dict[str, Any],
        memory: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        """
        Converts user input into structured reasoning plan
        """

        intent = self._detect_intent(user_message)

        sub_goals = self._generate_subgoals(user_message, intent)

        risk_level = self._estimate_complexity(
            user_message,
            context,
            memory
        )

        plan = {
            "intent": intent,
            "sub_goals": sub_goals,
            "complexity": risk_level,
            "requires_memory": len(memory) > 0,
            "context_relevance": context.get("context_strength", 0.5),
            "emotion": emotion.get("emotion", "neutral")
        }

        return plan

    # ========================================================
    # INTENT DETECTION
    # ========================================================

    def _detect_intent(self, text: str) -> str:

        text_lower = text.lower()

        for intent, patterns in self.intent_patterns.items():

            for pattern in patterns:

                if re.search(pattern, text_lower):

                    return intent

        return "general"

    # ========================================================
    # SUB-GOAL GENERATION
    # ========================================================

    def _generate_subgoals(
        self,
        text: str,
        intent: str
    ) -> List[str]:

        subgoals = []

        if intent == "learning":

            subgoals = [
                "Identify core concept",
                "Retrieve relevant memory context",
                "Explain step-by-step",
                "Provide examples"
            ]

        elif intent == "task":

            subgoals = [
                "Understand task requirements",
                "Check available context",
                "Generate solution steps",
                "Return structured output"
            ]

        elif intent == "analysis":

            subgoals = [
                "Break down query",
                "Retrieve supporting information",
                "Perform comparison reasoning",
                "Summarize insights"
            ]

        elif intent == "memory_query":

            subgoals = [
                "Search memory store",
                "Rank relevant memories",
                "Retrieve contextual history",
                "Summarize findings"
            ]

        else:

            subgoals = [
                "Understand user request",
                "Retrieve relevant context",
                "Generate helpful response"
            ]

        return subgoals

    # ========================================================
    # COMPLEXITY ESTIMATION
    # ========================================================

    def _estimate_complexity(
        self,
        text: str,
        context: Dict[str, Any],
        memory: List[Dict[str, Any]]
    ) -> float:

        score = 0.5

        # length-based complexity
        score += min(len(text.split()) / 50, 0.3)

        # memory load
        score += min(len(memory) / 10, 0.1)

        # context complexity
        try:
            if context.get("context_strength", 0) > 0.7:
                score += 0.1
        except:
            pass

        return float(min(score, 1.0))


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    planner = Planner()

    plan = planner.create_plan(

        user_message="I want to learn AI step by step",

        context={"context_strength": 0.8},

        emotion={"emotion": "joy"},

        memory=[
            {"memory": "User likes AI"},
            {"memory": "User studies ML"}
        ]
    )

    print("\n=== PLAN OUTPUT ===")
    print(plan)