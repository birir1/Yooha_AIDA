# ============================================================
# memory_summarizer.py
# Production-Grade Conversation Summarizer
# Optimized for Long-Term Memory Compression
# ============================================================

from typing import List, Dict, Optional
import threading

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)


# ============================================================
# MEMORY SUMMARIZER
# ============================================================

class MemorySummarizer:

    def __init__(
        self,
        model_name: str = "google/flan-t5-base",
        max_input_length: int = 1024
    ):

        print("🚀 Initializing Memory Summarizer...")

        # ====================================================
        # THREAD SAFETY
        # ====================================================

        self.lock = threading.Lock()

        # ====================================================
        # CONFIGURATION
        # ====================================================

        self.model_name = model_name
        self.max_input_length = max_input_length

        # ====================================================
        # DEVICE DETECTION
        # ====================================================

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(f"🖥️ Using device: {self.device}")

        # ====================================================
        # LOAD TOKENIZER
        # ====================================================

        print("📦 Loading tokenizer...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name
        )

        # ====================================================
        # MODEL LOADING
        # ====================================================

        print("📦 Loading summarization model...")

        model_kwargs = {}

        # GPU OPTIMIZATION
        if self.device == "cuda":

            model_kwargs.update({
                "device_map": "auto",
                "torch_dtype": torch.float16
            })

        # CPU SAFE MODE
        else:

            model_kwargs.update({
                "torch_dtype": torch.float32
            })

        self.model = (
            AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
        )

        # MOVE TO CPU MANUALLY IF NEEDED
        if self.device == "cpu":
            self.model.to(self.device)

        # EVAL MODE
        self.model.eval()

        print("✅ Summarization model loaded.")

    # ========================================================
    # BUILD CONVERSATION TEXT
    # ========================================================

    def build_conversation_text(
        self,
        conversation_history: List[Dict]
    ) -> str:

        lines = []

        for turn in conversation_history:

            # SUPPORT MULTIPLE FORMATS
            user_message = (
                turn.get("user_message")
                or turn.get("content", "")
            )

            assistant_message = (
                turn.get("assistant_response", "")
            )

            role = turn.get("role")

            # ================================================
            # CHAT MESSAGE FORMAT
            # ================================================

            if role == "user":

                lines.append(
                    f"User: {user_message}"
                )

            elif role == "assistant":

                lines.append(
                    f"Assistant: {user_message}"
                )

            # ================================================
            # STRUCTURED TURN FORMAT
            # ================================================

            else:

                if user_message:

                    lines.append(
                        f"User: {user_message}"
                    )

                if assistant_message:

                    lines.append(
                        f"Assistant: {assistant_message}"
                    )

        return "\n".join(lines)

    # ========================================================
    # SAFE TEXT TRUNCATION
    # ========================================================

    def _truncate_text(
        self,
        text: str
    ) -> str:

        tokens = self.tokenizer.encode(
            text,
            truncation=True,
            max_length=self.max_input_length
        )

        return self.tokenizer.decode(
            tokens,
            skip_special_tokens=True
        )

    # ========================================================
    # SUMMARIZATION
    # ========================================================

    @torch.no_grad()
    def summarize(
        self,
        conversation_history: List[Dict],
        max_new_tokens: int = 120,
        temperature: float = 0.3
    ) -> str:

        if not conversation_history:

            return "No conversation history available."

        with self.lock:

            try:

                # ============================================
                # BUILD CONVERSATION
                # ============================================

                conversation_text = (
                    self.build_conversation_text(
                        conversation_history
                    )
                )

                # ============================================
                # TRUNCATE SAFELY
                # ============================================

                conversation_text = (
                    self._truncate_text(
                        conversation_text
                    )
                )

                # ============================================
                # PROMPT ENGINEERING
                # ============================================

                prompt = f"""
Summarize the following conversation into concise memory points.

Focus on:
- personal preferences
- goals
- emotions
- interests
- important facts
- ongoing projects
- skills and education

Conversation:
{conversation_text}

Summary:
"""

                # ============================================
                # TOKENIZATION
                # ============================================

                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.max_input_length
                )

                # MOVE TO DEVICE
                inputs = {
                    k: v.to(self.model.device)
                    for k, v in inputs.items()
                }

                # ============================================
                # GENERATION
                # ============================================

                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=False,
                    num_beams=4,
                    repetition_penalty=1.2,
                    length_penalty=1.0,
                    early_stopping=True
                )

                # ============================================
                # DECODE
                # ============================================

                summary = self.tokenizer.decode(
                    outputs[0],
                    skip_special_tokens=True
                ).strip()

                # EMPTY GUARD
                if not summary:

                    return (
                        "Unable to generate summary."
                    )

                return summary

            except Exception as e:

                print(
                    f"[WARN] Summarization failed: {e}"
                )

                return (
                    "Summary generation failed."
                )

    # ========================================================
    # MEMORY POINT EXTRACTION
    # ========================================================

    def extract_memory_points(
        self,
        summary: str
    ) -> List[str]:

        if not summary:
            return []

        memory_points = []

        # SPLIT BY COMMON DELIMITERS
        chunks = (
            summary
            .replace("\n", ".")
            .split(".")
        )

        for chunk in chunks:

            cleaned = chunk.strip()

            if len(cleaned) > 5:

                memory_points.append(cleaned)

        # REMOVE DUPLICATES
        unique = []

        seen = set()

        for point in memory_points:

            normalized = point.lower()

            if normalized not in seen:

                seen.add(normalized)
                unique.append(point)

        return unique

    # ========================================================
    # SHORT SUMMARY
    # ========================================================

    def short_summary(
        self,
        conversation_history: List[Dict]
    ) -> str:

        return self.summarize(
            conversation_history=conversation_history,
            max_new_tokens=60,
            temperature=0.2
        )

    # ========================================================
    # DETAILED SUMMARY
    # ========================================================

    def detailed_summary(
        self,
        conversation_history: List[Dict]
    ) -> str:

        return self.summarize(
            conversation_history=conversation_history,
            max_new_tokens=200,
            temperature=0.3
        )

    # ========================================================
    # STRUCTURED MEMORY SUMMARY
    # ========================================================

    def memory_summary(
        self,
        conversation_history: List[Dict]
    ) -> Dict:

        summary = self.short_summary(
            conversation_history
        )

        points = self.extract_memory_points(
            summary
        )

        return {
            "summary": summary,
            "memory_points": points,
            "memory_count": len(points)
        }

    # ========================================================
    # MODEL INFO
    # ========================================================

    def get_model_info(self) -> Dict:

        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_input_length": self.max_input_length
        }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    sample_history = [

        {
            "user_message":
                "I love studying cybersecurity.",
            "assistant_response":
                "That is a valuable field."
        },

        {
            "user_message":
                "I want to become an AI engineer.",
            "assistant_response":
                "That is an excellent career goal."
        },

        {
            "user_message":
                "I enjoy coffee while coding.",
            "assistant_response":
                "Coffee helps many developers focus."
        }
    ]

    summarizer = MemorySummarizer()

    summary = summarizer.summarize(
        sample_history
    )

    print("\n=== SUMMARY ===\n")
    print(summary)

    print("\n=== MEMORY POINTS ===\n")

    memory_points = (
        summarizer.extract_memory_points(
            summary
        )
    )

    for idx, point in enumerate(memory_points):

        print(f"{idx + 1}. {point}")

    print("\n=== MODEL INFO ===\n")
    print(
        summarizer.get_model_info()
    )