# ============================================================
# llm_service.py
# AIDA PRODUCTION LLM SERVICE
# ULTRA STABLE + EMOTIONALLY AWARE + HUMAN RESPONSES
# ============================================================

import re
import random
import logging
import torch

from typing import Dict, List, Optional, Any

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)

from peft import PeftModel

logger = logging.getLogger(__name__)

# ============================================================
# CONFIG
# ============================================================

BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

LORA_PATH = "models/llm/lora_finetuned"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MAX_NEW_TOKENS = 140

# ============================================================
# EMOTION STYLES
# ============================================================

EMOTION_STYLES = {

    "anger":
        "Stay calm, grounding, patient, emotionally steady, and mature.",

    "disgust":
        "Be composed, understanding, emotionally intelligent, and respectful.",

    "fear":
        "Be reassuring, comforting, gentle, calming, and supportive.",

    "joy":
        "Be upbeat, warm, friendly, encouraging, and energetic.",

    "sadness":
        "Be emotionally warm, validating, caring, soft, and understanding.",

    "surprise":
        "Be curious, attentive, conversational, and engaged.",

    "neutral":
        "Be natural, relaxed, conversational, and friendly."
}

# ============================================================
# LLM SERVICE
# ============================================================

class LLMService:

    def __init__(self):

        logger.info("🚀 Loading tokenizer...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL,
            trust_remote_code=True
        )

        self.tokenizer.pad_token = self.tokenizer.eos_token

        logger.info("🚀 Loading quantized base model...")

        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )

        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=quant_config,
            device_map="auto",
            trust_remote_code=True
        )

        logger.info("🚀 Loading LoRA adapters...")

        self.model = PeftModel.from_pretrained(
            base_model,
            LORA_PATH
        )

        self.model.eval()

        logger.info("✅ AIDA model ready")

    # ========================================================
    # MAIN RESPONSE GENERATION
    # ========================================================

    def generate_response(
        self,
        user_message: str,
        context: str = "",
        emotion: Optional[str] = None,
        memories: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:

        try:

            memories = memories or []
            conversation_history = conversation_history or []

            emotion = self.normalize_emotion(
                emotion or "neutral"
            )

            # ====================================================
            # SMART SHORT-CIRCUIT HUMAN RESPONSES
            # ====================================================

            fast_response = self.quick_emotional_response(
                user_message,
                emotion
            )

            if fast_response:
                return fast_response

            # ====================================================
            # PROMPT
            # ====================================================

            prompt = self.build_prompt(
                user_message=user_message,
                context=context,
                emotion=emotion,
                memories=memories,
                conversation_history=conversation_history
            )

            logger.info("🧠 Generating AIDA response...")

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.model.device)

            with torch.no_grad():

                outputs = self.model.generate(

                    **inputs,

                    max_new_tokens=MAX_NEW_TOKENS,

                    temperature=0.72,
                    top_p=0.92,
                    top_k=40,

                    repetition_penalty=1.18,

                    no_repeat_ngram_size=4,

                    do_sample=True,

                    eos_token_id=self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            decoded = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )

            response = self.extract_response(
                decoded,
                prompt
            )

            response = self.clean_response(response)

            response = self.validate_response(
                response,
                emotion
            )

            logger.info("✅ Response generated")

            return response

        except Exception:

            logger.exception("❌ Generation failed")

            return self.safe_fallback_response(
                user_message,
                emotion or "neutral"
            )

    # ========================================================
    # QUICK HUMAN RESPONSES
    # ========================================================

    def quick_emotional_response(
        self,
        message: str,
        emotion: str
    ) -> Optional[str]:

        msg = message.lower().strip()

        # ====================================================
        # GREETINGS
        # ====================================================

        greetings = [
            "hi",
            "hello",
            "hey",
            "hallo",
            "yo"
        ]

        if msg in greetings:

            responses = [
                "Hey, how are you feeling today?",
                "Hi there. What's been on your mind lately?",
                "Hey, good to hear from you.",
                "Hello :) how's your day going?",
                "Hey there. How are things today?"
            ]

            return random.choice(responses)

        # ====================================================
        # SADNESS
        # ====================================================

        sadness_words = [
            "sad",
            "lonely",
            "depressed",
            "low",
            "empty",
            "hurt"
        ]

        if any(word in msg for word in sadness_words):

            responses = [
                "I'm sorry things feel heavy right now. Want to talk about it a bit?",
                "That sounds rough honestly. I'm here with you.",
                "I get you. Some days really do feel overwhelming.",
                "You don't have to carry all of that alone.",
                "I'm listening. What's been making things hard lately?"
            ]

            return random.choice(responses)

        # ====================================================
        # FEAR / ANXIETY
        # ====================================================

        anxiety_words = [
            "anxiety",
            "afraid",
            "fear",
            "scared",
            "exam",
            "stressed",
            "stress"
        ]

        if any(word in msg for word in anxiety_words):

            responses = [
                "Exams can seriously mess with your head sometimes. But you're not failing just because you're anxious.",
                "That pressure can feel exhausting honestly. Let's handle it one step at a time.",
                "You're probably more capable than your anxiety is telling you right now.",
                "It's okay to feel nervous before exams. A lot of people do.",
                "Alright, let's slow it down a little. What's stressing you the most?"
            ]

            return random.choice(responses)

        # ====================================================
        # FRIENDSHIP / RAPPORT
        # ====================================================

        if "friend" in msg:

            return (
                "Of course. We can just talk normally here. "
                "What's been going on with you lately?"
            )

        # ====================================================
        # RELATIONSHIPS
        # ====================================================

        relationship_words = [
            "girlfriend",
            "relationship",
            "single"
        ]

        if any(word in msg for word in relationship_words):

            responses = [
                "That stuff can really get into your head sometimes, especially when you feel behind compared to other people.",
                "Honestly, not having a relationship right now doesn't mean something is wrong with you.",
                "A lot of people quietly feel that same pressure.",
                "I get why that would bother you though.",
                "Relationships happen at different times for different people."
            ]

            return random.choice(responses)

        return None

    # ========================================================
    # PROMPT BUILDER
    # ========================================================

    def build_prompt(
        self,
        user_message: str,
        context: str,
        emotion: str,
        memories: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]]
    ) -> str:

        memory_text = ""

        for memory in memories[:5]:

            try:

                if isinstance(memory, dict):

                    content = (
                        memory.get("content")
                        or memory.get("memory")
                        or memory.get("text")
                        or ""
                    )

                else:
                    content = str(memory)

                if content:
                    memory_text += f"- {content}\n"

            except Exception:
                continue

        history_text = ""

        for msg in conversation_history[-8:]:

            role = msg.get("role", "user")
            text = msg.get("text", "")

            if not text:
                continue

            if role == "user":
                history_text += f"User: {text}\n"
            else:
                history_text += f"AIDA: {text}\n"

        emotion_style = EMOTION_STYLES.get(
            emotion,
            EMOTION_STYLES["neutral"]
        )

        return f"""
You are AIDA.

AIDA is:
- emotionally intelligent
- emotionally aware
- supportive
- conversational
- warm
- natural
- calm
- human-like
- emotionally mature
- good at building rapport

IMPORTANT RULES:
- Talk naturally like a real supportive friend
- NEVER output labels
- NEVER output "User:" or "Assistant:"
- NEVER output IDs, variables, symbols, placeholders, or artifacts
- NEVER repeat the user's words awkwardly
- NEVER sound robotic
- NEVER give generic AI disclaimers
- NEVER mention being an AI unless directly asked
- Keep responses concise and emotionally natural
- Sound emotionally present and attentive
- Avoid overexplaining
- Avoid therapy-style robotic language
- Respond like texting a friend naturally

CURRENT EMOTION:
{emotion}

RESPONSE STYLE:
{emotion_style}

MEMORIES:
{memory_text if memory_text else "None"}

CONTEXT:
{context if context else "None"}

RECENT CHAT:
{history_text if history_text else "None"}

USER MESSAGE:
{user_message}

AIDA RESPONSE:
""".strip()

    # ========================================================
    # EXTRACT RESPONSE
    # ========================================================

    def extract_response(
        self,
        decoded: str,
        prompt: str
    ) -> str:

        if decoded.startswith(prompt):
            decoded = decoded[len(prompt):]

        markers = [

            "USER:",
            "User:",
            "SYSTEM:",
            "ASSISTANT:",
            "Assistant:",
            "AIDA RESPONSE:",
            "AIDA:",
            "\nUser:",
            "\nUSER:"
        ]

        for marker in markers:

            if marker in decoded:
                decoded = decoded.split(marker)[0]

        return decoded.strip()

    # ========================================================
    # CLEAN RESPONSE
    # ========================================================

    def clean_response(self, text: str) -> str:

        if not text:
            return ""

        text = re.sub(r"\s+", " ", text)

        garbage_patterns = [

            r"\bUser\b",
            r"\bUSER\b",
            r"\bAssistant\b",
            r"\bassistant\b",
            r"\bcustomer\b",
            r"\bundefined\b",
            r"\bnull\b",
            r"\bAIDA RESPONSE\b",
            r"\bAIDA\b\s*:",
            r"\d+:\d+",
            r"\{\:.*?\}",
            r"<.*?>",
            r"\[.*?\]",
            r"Message",
            r"Response",
            r"Experience",
            r"Friendly",
            r"Assessment",
            r"Assist"
        ]

        for pattern in garbage_patterns:

            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE
            )

        text = text.replace("�", "")

        text = text.replace(" .", ".")
        text = text.replace(" ,", ",")
        text = text.replace("..", ".")
        text = text.replace("  ", " ")

        text = text.strip()

        # Remove broken sentence starts
        broken_starts = [
            "and ",
            "but ",
            "or ",
            "so "
        ]

        lower = text.lower()

        for start in broken_starts:

            if lower.startswith(start):
                text = text[len(start):]

        return text.strip(" -,:;")

    # ========================================================
    # VALIDATE RESPONSE
    # ========================================================

    def validate_response(
        self,
        response: str,
        emotion: str
    ) -> str:

        if not response:

            return self.safe_fallback_response(
                "",
                emotion
            )

        lower = response.lower()

        bad_phrases = [

            "how ful",
            "what kind of motivation",
            "did you just get",
            "friendly study plan",
            "experience:",
            "assistant:",
            "user:",
            "customer",
            "undefined",
            "null",
            "aida:",
            "message:",
            "response:",
            "userx",
            "usery"
        ]

        for phrase in bad_phrases:

            if phrase in lower:

                return self.safe_fallback_response(
                    "",
                    emotion
                )

        if len(response.split()) < 4:

            return self.safe_fallback_response(
                "",
                emotion
            )

        return response[:450]

    # ========================================================
    # NORMALIZE EMOTION
    # ========================================================

    def normalize_emotion(
        self,
        emotion: str
    ) -> str:

        emotion = str(emotion).lower()

        mapping = {

            "anger": "anger",
            "annoyance": "anger",
            "disapproval": "anger",

            "disgust": "disgust",

            "fear": "fear",
            "nervousness": "fear",

            "joy": "joy",
            "amusement": "joy",
            "approval": "joy",
            "caring": "joy",
            "desire": "joy",
            "excitement": "joy",
            "gratitude": "joy",
            "love": "joy",
            "optimism": "joy",
            "pride": "joy",
            "relief": "joy",
            "admiration": "joy",

            "sadness": "sadness",
            "disappointment": "sadness",
            "embarrassment": "sadness",
            "grief": "sadness",
            "remorse": "sadness",

            "surprise": "surprise",
            "realization": "surprise",
            "confusion": "surprise",
            "curiosity": "surprise",

            "neutral": "neutral"
        }

        return mapping.get(
            emotion,
            "neutral"
        )

    # ========================================================
    # SAFE FALLBACKS
    # ========================================================

    def safe_fallback_response(
        self,
        message: str,
        emotion: str
    ) -> str:

        emotion = self.normalize_emotion(emotion)

        if emotion == "sadness":

            options = [

                "That sounds really heavy right now. I'm here with you.",
                "I'm sorry things feel rough right now.",
                "You don't have to deal with everything alone.",
                "That honestly sounds exhausting emotionally."
            ]

            return random.choice(options)

        if emotion == "fear":

            options = [

                "You're under a lot of pressure right now, aren't you?",
                "Take it one step at a time. You don't have to solve everything at once.",
                "Anxiety can make things feel worse than they really are sometimes.",
                "You've probably handled harder things before without realizing it."
            ]

            return random.choice(options)

        if emotion == "anger":

            return (
                "I can tell something is really frustrating you right now."
            )

        lowered = message.lower()

        if "hello" in lowered or "hi" in lowered:

            return (
                "Hey, good to hear from you."
            )

        if "exam" in lowered:

            return (
                "Okay, let's tackle this together. "
                "What's the hardest subject right now?"
            )

        if "lonely" in lowered:

            return (
                "I'm here with you. "
                "Want to talk for a bit?"
            )

        return (
            "I'm listening. "
            "Tell me more."
        )

    # ========================================================
    # HEALTH
    # ========================================================

    def health(self):

        return True


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

OllamaLLMService = LLMService