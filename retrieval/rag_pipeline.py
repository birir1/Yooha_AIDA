# ============================================================
# rag_pipeline.py (PRODUCTION FIXED + BACKWARD COMPATIBLE)
# ============================================================

from typing import Dict, List, Any, Optional
import math
import re


class RAGPipeline:

    def __init__(self):

        print("🚀 Initializing RAG Pipeline (Fixed + Backward Compatible)...")

        self.weights = {
            "memory": 0.45,
            "retrieval": 0.35,
            "recency": 0.20
        }

        print("✅ RAG Pipeline Ready.")

    # ============================================================
    # MAIN ENTRY (NOW FULLY FLEXIBLE)
    # ============================================================

    def run(
        self,
        user_message: str = "",
        memory_results: Optional[List[Dict[str, Any]]] = None,
        retrieval_results: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        # 🔴 BACKWARD COMPATIBILITY (IGNORE SAFELY)
        memories: Optional[Any] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        top_k: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:

        """
        FIX:
        - Accepts ALL unexpected kwargs safely
        - Prevents crash from chat_routes.py
        - Maintains backward compatibility
        """

        memory_results = memory_results or memories or []
        retrieval_results = retrieval_results or []
        context = context or {}

        # Ensure safe types
        if memory_results is None:
            memory_results = []
        if retrieval_results is None:
            retrieval_results = []

        # ========================================================
        # SCORING
        # ========================================================

        memory_score = self._score_memory(memory_results)
        retrieval_score = self._score_retrieval(retrieval_results)
        recency_score = self._score_recency(memory_results, retrieval_results)
        alignment_score = self._semantic_alignment_bonus(
            user_message,
            memory_results,
            retrieval_results
        )

        fused_score = self._fuse(
            memory_score,
            retrieval_score,
            recency_score,
            alignment_score
        )

        context_block = self._build_context_block(
            memory_results,
            retrieval_results
        )

        return {
            "fused_score": round(fused_score, 4),
            "memory_score": round(memory_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "recency_score": round(recency_score, 4),
            "alignment_score": round(alignment_score, 4),
            "context_block": context_block,
            "context_summary": self._build_summary(
                memory_results,
                retrieval_results,
                fused_score
            )
        }

    # ============================================================
    # SAFE TEXT EXTRACTION
    # ============================================================

    def _get_text(self, item: Dict[str, Any]) -> str:
        if not isinstance(item, dict):
            return str(item)

        return (
            item.get("memory")
            or item.get("text")
            or item.get("content")
            or ""
        )

    # ============================================================
    # MEMORY SCORING
    # ============================================================

    def _score_memory(self, memory_results):
        if not memory_results:
            return 0.5

        scores = []
        for m in memory_results:
            if isinstance(m, dict):
                scores.append(float(m.get("score", m.get("final_score", 0.5))))
            else:
                scores.append(0.5)

        return sum(scores) / len(scores)

    # ============================================================
    # RETRIEVAL SCORING
    # ============================================================

    def _score_retrieval(self, retrieval_results):
        if not retrieval_results:
            return 0.5

        scores = []
        for r in retrieval_results:
            if isinstance(r, dict):
                scores.append(float(r.get("score", r.get("final_score", 0.5))))
            else:
                scores.append(0.5)

        return sum(scores) / len(scores)

    # ============================================================
    # RECENCY SIGNAL
    # ============================================================

    def _score_recency(self, memory_results, retrieval_results):
        total = len(memory_results) + len(retrieval_results)

        if total == 0:
            return 0.5

        return 1.0 / (1.0 + math.log1p(total))

    # ============================================================
    # SEMANTIC ALIGNMENT
    # ============================================================

    def _clean_tokens(self, text: str) -> set:
        text = str(text).lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return set(text.split())

    def _semantic_alignment_bonus(self, user_message, memory_results, retrieval_results):

        if not user_message:
            return 0.5

        user_tokens = self._clean_tokens(user_message)

        if not user_tokens:
            return 0.5

        all_texts = []

        for m in memory_results:
            all_texts.append(self._get_text(m))

        for r in retrieval_results:
            all_texts.append(self._get_text(r))

        scores = []

        for text in all_texts:
            tokens = self._clean_tokens(text)

            if not tokens:
                continue

            overlap = len(user_tokens.intersection(tokens))
            score = overlap / max(len(user_tokens), 1)

            if score > 0:
                scores.append(min(1.0, score * 2))

        if not scores:
            return 0.5

        return sum(scores) / len(scores)

    # ============================================================
    # FUSION ENGINE
    # ============================================================

    def _fuse(self, memory_score, retrieval_score, recency_score, alignment_score):

        fused = (
            memory_score * self.weights["memory"] +
            retrieval_score * self.weights["retrieval"] +
            recency_score * self.weights["recency"] +
            alignment_score * 0.10
        )

        return max(0.0, min(1.0, fused))

    # ============================================================
    # CONTEXT BUILDER
    # ============================================================

    def _build_context_block(self, memory_results, retrieval_results):

        lines = ["=== MEMORY CONTEXT ==="]

        if memory_results:
            for m in memory_results:
                lines.append(f"- {self._get_text(m)}")
        else:
            lines.append("- No memory context found")

        lines.append("\n=== RETRIEVAL CONTEXT ===")

        if retrieval_results:
            for r in retrieval_results:
                lines.append(f"- {self._get_text(r)}")
        else:
            lines.append("- No retrieval context found")

        return "\n".join(lines)

    # ============================================================
    # SUMMARY
    # ============================================================

    def _build_summary(self, memory_results, retrieval_results, score):

        return (
            f"Memory items: {len(memory_results)} | "
            f"Retrieval items: {len(retrieval_results)} | "
            f"Context strength: {round(score, 3)}"
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    rag = RAGPipeline()

    result = rag.run(
        user_message="I want to learn AI",
        memories=[{"memory": "User likes AI", "score": 0.9}],
        retrieval_results=[{"text": "AI is a field", "score": 0.7}]
    )

    print(result)