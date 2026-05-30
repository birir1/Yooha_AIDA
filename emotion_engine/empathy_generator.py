# ============================================================
# empathy_generator.py
# Generates empathetic responses
# ============================================================

from typing import Dict, Optional

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)

from emotion_engine.emotion_detector import (
    EmotionDetector
)


class EmpathyGenerator:

    def __init__(self):

        self.model_name = (
            "microsoft/DialoGPT-medium"
        )

        print("Loading empathetic response model...")

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                self.model_name
            )
        )

        self.model = (
            AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.float16
            )
        )

        print("Empathy model loaded.")

        self.emotion_detector = (
            EmotionDetector()
        )

        self.empathy_prefix = {

            "sadness":
                "I'm sorry you're going through that. ",

            "anger":
                "That sounds really frustrating. ",

            "fear":
                "I understand why that could feel worrying. ",

            "joy":
                "That's wonderful to hear! ",

            "surprise":
                "That sounds surprising. ",

            "neutral":
                ""
        }

    # ========================================================
    # BUILD PROMPT
    # ========================================================

    def build_prompt(
        self,
        user_message: str,
        emotion: str,
        memory_context: Optional[str] = None
    ) -> str:

        prompt_parts = []

        if memory_context:

            prompt_parts.append(
                f"Context:\n{memory_context}"
            )

        prompt_parts.append(
            f"User Emotion: {emotion}"
        )

        prompt_parts.append(
            f"User Message: {user_message}"
        )

        prompt_parts.append(
            "Assistant:"
        )

        return "\n\n".join(prompt_parts)

    # ========================================================
    # GENERATE RESPONSE
    # ========================================================

    def generate_response(
        self,
        user_message: str,
        memory_context: Optional[str] = None,
        max_new_tokens: int = 80
    ) -> Dict:

        # ----------------------------------------------------
        # Emotion Detection
        # ----------------------------------------------------

        emotion_result = (
            self.emotion_detector
            .detect_emotion(user_message)
        )

        emotion = emotion_result["emotion"]

        confidence = (
            emotion_result["confidence"]
        )

        # ----------------------------------------------------
        # Build Prompt
        # ----------------------------------------------------

        prompt = self.build_prompt(
            user_message=user_message,
            emotion=emotion,
            memory_context=memory_context
        )

        # ----------------------------------------------------
        # Tokenization
        # ----------------------------------------------------

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.model.device)

        # ----------------------------------------------------
        # Generation
        # ----------------------------------------------------

        outputs = self.model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=max_new_tokens,
            temperature=0.8,
            top_p=0.9,
            do_sample=True,
            repetition_penalty=1.1,
            pad_token_id=
                self.tokenizer.eos_token_id
        )

        decoded = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        # ----------------------------------------------------
        # Extract assistant response
        # ----------------------------------------------------

        if "Assistant:" in decoded:

            generated_response = (
                decoded.split("Assistant:")[-1]
                .strip()
            )

        else:

            generated_response = decoded.strip()

        # ----------------------------------------------------
        # Add empathy prefix
        # ----------------------------------------------------

        prefix = self.empathy_prefix.get(
            emotion,
            ""
        )

        final_response = (
            prefix + generated_response
        )

        return {

            "response": final_response,

            "emotion": emotion,

            "confidence": confidence
        }

    # ========================================================
    # SAFE RESPONSE CLEANUP
    # ========================================================

    def clean_response(
        self,
        response: str
    ) -> str:

        response = response.replace(
            "\n",
            " "
        )

        response = response.strip()

        while "  " in response:

            response = response.replace(
                "  ",
                " "
            )

        return response

    # ========================================================
    # GENERATE CLEAN RESPONSE
    # ========================================================

    def empathetic_chat(
        self,
        user_message: str,
        memory_context: Optional[str] = None
    ) -> Dict:

        result = self.generate_response(
            user_message=user_message,
            memory_context=memory_context
        )

        result["response"] = (
            self.clean_response(
                result["response"]
            )
        )

        return result


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":

    generator = EmpathyGenerator()

    test_messages = [

        "I failed my exams and feel terrible.",

        "I just got my dream job today!",

        "I'm stressed about my future.",

        "I feel lonely lately."
    ]

    for msg in test_messages:

        print("\n" + "=" * 70)

        print(f"USER: {msg}")

        result = generator.empathetic_chat(
            user_message=msg
        )

        print("\nDETECTED EMOTION:")
        print(result["emotion"])

        print("\nASSISTANT RESPONSE:")
        print(result["response"])