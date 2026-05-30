# ============================================================
# response_generator.py
# Advanced Emotionally Intelligent Response Generator
# Memory-Augmented Reasoning Engine
# ============================================================

import logging
import torch

from typing import List, Dict, Optional, Any

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)

if not logger.handlers:

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"


# ============================================================
# RESPONSE GENERATOR
# ============================================================

class ResponseGenerator:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        logger.info(
            "🚀 Initializing Response Generator..."
        )

        # ====================================================
        # TOKENIZER
        # ====================================================

        logger.info(
            "📦 Loading tokenizer..."
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

        if self.tokenizer.pad_token is None:

            self.tokenizer.pad_token = (
                self.tokenizer.eos_token
            )

        # ====================================================
        # QUANTIZATION CONFIG
        # ====================================================

        bnb_config = BitsAndBytesConfig(

            load_in_4bit=True,

            bnb_4bit_quant_type="nf4",

            bnb_4bit_compute_dtype=torch.float16,

            bnb_4bit_use_double_quant=True
        )

        # ====================================================
        # MODEL LOADING
        # ====================================================

        logger.info(
            "📦 Loading language model..."
        )

        self.model = (
            AutoModelForCausalLM.from_pretrained(

                MODEL_NAME,

                quantization_config=bnb_config,

                device_map="auto",

                torch_dtype=torch.float16
            )
        )

        self.model.eval()

        logger.info(
            "✅ Response Generator Ready"
        )

    # ========================================================
    # MAIN RESPONSE GENERATION
    # ========================================================

    def generate_response(

        self,

        user_message: str,

        retrieved_memories: Optional[
            List[Dict[str, Any]]
        ] = None,

        emotion: Optional[str] = None,

        conversation_history: Optional[
            List[Dict[str, str]]
        ] = None,

        context: Optional[str] = None,

        max_new_tokens: int = 220
    ) -> str:

        try:

            # ================================================
            # INTENT DETECTION
            # ================================================

            intent = self.detect_intent(
                user_message
            )

            # ================================================
            # MEMORY PRIORITIZATION
            # ================================================

            prioritized_memories = (
                self.prioritize_memories(
                    retrieved_memories
                )
            )

            # ================================================
            # PROMPT CONSTRUCTION
            # ================================================

            prompt = self.build_prompt(

                user_message=user_message,

                retrieved_memories=(
                    prioritized_memories
                ),

                emotion=emotion,

                intent=intent,

                conversation_history=(
                    conversation_history
                ),

                context=context
            )

            # ================================================
            # TOKENIZATION
            # ================================================

            inputs = self.tokenizer(

                prompt,

                return_tensors="pt",

                padding=True,

                truncation=True,

                max_length=4096
            )

            # ================================================
            # MOVE TO DEVICE
            # ================================================

            inputs = {

                key: value.to(
                    self.model.device
                )

                for key, value
                in inputs.items()
            }

            # ================================================
            # GENERATION CONFIG
            # ================================================

            generation_config = (
                self.get_generation_config(
                    emotion=emotion,
                    intent=intent
                )
            )

            # ================================================
            # GENERATE
            # ================================================

            with torch.no_grad():

                outputs = self.model.generate(

                    input_ids=inputs[
                        "input_ids"
                    ],

                    attention_mask=inputs[
                        "attention_mask"
                    ],

                    max_new_tokens=max_new_tokens,

                    temperature=(
                        generation_config[
                            "temperature"
                        ]
                    ),

                    top_p=(
                        generation_config[
                            "top_p"
                        ]
                    ),

                    do_sample=True,

                    repetition_penalty=1.15,

                    pad_token_id=(
                        self.tokenizer
                        .eos_token_id
                    )
                )

            # ================================================
            # DECODE
            # ================================================

            generated_text = (
                self.tokenizer.decode(

                    outputs[0],

                    skip_special_tokens=True
                )
            )

            # ================================================
            # CLEAN RESPONSE
            # ================================================

            response = (
                self.extract_response(

                    generated_text,

                    prompt
                )
            )

            # ================================================
            # POST PROCESSING
            # ================================================

            response = self.post_process_response(
                response
            )

            # ================================================
            # VALIDATION
            # ================================================

            response = self.validate_response(
                response
            )

            return response

        except Exception as e:

            logger.exception(
                "Response generation failed"
            )

            return (
                "I encountered an issue while "
                "processing your request. "
                "Please try again."
            )

    # ========================================================
    # PROMPT BUILDER
    # ========================================================

    def build_prompt(

        self,

        user_message: str,

        retrieved_memories: Optional[
            List[Dict[str, Any]]
        ] = None,

        emotion: Optional[str] = None,

        intent: Optional[str] = None,

        conversation_history: Optional[
            List[Dict[str, str]]
        ] = None,

        context: Optional[str] = None
    ) -> str:

        system_prompt = (
            self.get_system_prompt(
                intent=intent,
                emotion=emotion
            )
        )

        # ====================================================
        # MEMORY SECTION
        # ====================================================

        memory_section = (
            self.build_memory_section(
                retrieved_memories
            )
        )

        # ====================================================
        # EMOTIONAL GUIDANCE
        # ====================================================

        emotional_guidance = (
            self.get_emotional_guidance(
                emotion
            )
        )

        # ====================================================
        # CONVERSATION HISTORY
        # ====================================================

        history_section = (
            self.build_history_section(
                conversation_history
            )
        )

        # ====================================================
        # CONTEXT SECTION
        # ====================================================

        context_section = ""

        if context:

            context_section = f"""

==================================================
CONTEXT WINDOW
==================================================

{context}
"""

        # ====================================================
        # FINAL PROMPT
        # ====================================================

        prompt = f"""

{system_prompt}

==================================================
USER EMOTION
==================================================

{emotion or "neutral"}

==================================================
INTENT
==================================================

{intent}

==================================================
EMOTIONAL RESPONSE STRATEGY
==================================================

{emotional_guidance}

{memory_section}

{context_section}

{history_section}

==================================================
CURRENT USER MESSAGE
==================================================

User: {user_message}

==================================================
ASSISTANT RESPONSE RULES
==================================================

- Be conversational and emotionally intelligent
- Avoid robotic responses
- Maintain conversational continuity
- Use relevant memory naturally
- Never invent false memories
- Avoid hallucinations
- Be empathetic when necessary
- Provide clear and coherent responses
- Be supportive and adaptive
- Avoid repetition
- Maintain realism and accuracy

Assistant:
"""

        return prompt.strip()

    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    def get_system_prompt(

        self,

        intent: Optional[str],

        emotion: Optional[str]
    ) -> str:

        return """

You are a memory-augmented emotionally intelligent AI assistant.

You maintain:
- long-term memory
- contextual awareness
- emotional intelligence
- conversational continuity
- adaptive reasoning

You are designed to:
- provide meaningful conversations
- remember relevant user information
- adapt to emotional states
- reason intelligently
- support users naturally

You are NOT a generic chatbot.

You are a personalized intelligent assistant capable of long-term interaction and emotional awareness.

""".strip()

    # ========================================================
    # INTENT DETECTION
    # ========================================================

    def detect_intent(
        self,
        text: str
    ) -> str:

        text = text.lower()

        intent_patterns = {

            "emotional_support": [

                "sad",
                "depressed",
                "stressed",
                "anxious",
                "upset",
                "hurt"
            ],

            "technical_question": [

                "code",
                "python",
                "ai",
                "machine learning",
                "cybersecurity",
                "algorithm"
            ],

            "planning": [

                "plan",
                "roadmap",
                "schedule",
                "future",
                "goal"
            ],

            "memory_recall": [

                "remember",
                "recall",
                "what did i say",
                "do you remember"
            ],

            "casual_conversation": [

                "hello",
                "hi",
                "how are you",
                "hey"
            ]
        }

        for intent, keywords in (
            intent_patterns.items()
        ):

            if any(
                keyword in text
                for keyword in keywords
            ):

                return intent

        return "general_reasoning"

    # ========================================================
    # MEMORY PRIORITIZATION
    # ========================================================

    def prioritize_memories(
        self,
        memories
    ):

        if not memories:
            return []

        sorted_memories = sorted(

            memories,

            key=lambda x: x.get(
                "final_score",
                x.get("score", 0)
            ),

            reverse=True
        )

        return sorted_memories[:6]

    # ========================================================
    # MEMORY SECTION
    # ========================================================

    def build_memory_section(
        self,
        memories
    ) -> str:

        if not memories:

            return """

==================================================
RELEVANT MEMORIES
==================================================

No relevant memories available.
"""

        lines = [

            """

==================================================
RELEVANT MEMORIES
==================================================
"""
        ]

        for idx, memory in enumerate(
            memories,
            start=1
        ):

            if isinstance(memory, dict):

                memory_text = memory.get(
                    "memory",
                    str(memory)
                )

                score = round(

                    memory.get(
                        "final_score",
                        memory.get("score", 0)
                    ),

                    3
                )

            else:

                memory_text = str(memory)

                score = 0.50

            lines.append(
                f"{idx}. "
                f"[relevance={score}] "
                f"{memory_text}"
            )

        return "\n".join(lines)

    # ========================================================
    # CONVERSATION HISTORY
    # ========================================================

    def build_history_section(
        self,
        history
    ) -> str:

        if not history:

            return """

==================================================
RECENT CONVERSATION
==================================================

No recent conversation history.
"""

        lines = [

            """

==================================================
RECENT CONVERSATION
==================================================
"""
        ]

        for item in history[-6:]:

            user_msg = item.get(
                "user",
                ""
            )

            assistant_msg = item.get(
                "assistant",
                ""
            )

            if user_msg:

                lines.append(
                    f"User: {user_msg}"
                )

            if assistant_msg:

                lines.append(
                    f"Assistant: "
                    f"{assistant_msg}"
                )

        return "\n".join(lines)

    # ========================================================
    # EMOTIONAL GUIDANCE
    # ========================================================

    def get_emotional_guidance(
        self,
        emotion
    ) -> str:

        if not emotion:

            return (
                "Maintain a balanced and "
                "natural conversational tone."
            )

        emotion = emotion.lower()

        guidance = {

            "sadness": (
                "Respond gently and supportively."
            ),

            "joy": (
                "Respond warmly and positively."
            ),

            "anger": (
                "Remain calm and patient."
            ),

            "fear": (
                "Use reassuring language."
            ),

            "stress": (
                "Provide calm and structured help."
            ),

            "anxiety": (
                "Be grounding and reassuring."
            ),

            "excitement": (
                "Match the user's enthusiasm."
            )
        }

        return guidance.get(

            emotion,

            "Maintain a balanced tone."
        )

    # ========================================================
    # GENERATION CONFIG
    # ========================================================

    def get_generation_config(

        self,

        emotion=None,

        intent=None
    ):

        config = {

            "temperature": 0.7,

            "top_p": 0.9
        }

        # ====================================================
        # EMOTIONAL ADAPTATION
        # ====================================================

        if emotion in [

            "sadness",
            "fear",
            "anxiety"
        ]:

            config["temperature"] = 0.55

        elif emotion in [

            "joy",
            "excitement"
        ]:

            config["temperature"] = 0.85

        # ====================================================
        # INTENT ADAPTATION
        # ====================================================

        if intent == "technical_question":

            config["temperature"] = 0.45

        elif intent == "casual_conversation":

            config["temperature"] = 0.80

        return config

    # ========================================================
    # RESPONSE EXTRACTION
    # ========================================================

    def extract_response(
        self,
        generated_text,
        prompt
    ):

        response = generated_text.replace(
            prompt,
            ""
        ).strip()

        unwanted_prefixes = [

            "Assistant:",
            "AI:",
            "Response:"
        ]

        for prefix in unwanted_prefixes:

            if response.startswith(prefix):

                response = response.replace(
                    prefix,
                    "",
                    1
                ).strip()

        return response

    # ========================================================
    # POST PROCESSING
    # ========================================================

    def post_process_response(
        self,
        response
    ):

        if not response:

            return (
                "I am here and ready to help."
            )

        lines = response.splitlines()

        cleaned = []

        previous = None

        for line in lines:

            normalized = line.strip()

            if (
                normalized
                and normalized != previous
            ):

                cleaned.append(line)

            previous = normalized

        return "\n".join(cleaned).strip()

    # ========================================================
    # RESPONSE VALIDATION
    # ========================================================

    def validate_response(
        self,
        response
    ):

        if not response:

            return (
                "I could not generate "
                "a response."
            )

        if len(response) < 2:

            return (
                "Could you clarify your request?"
            )

        max_length = 3500

        if len(response) > max_length:

            response = response[:max_length]

        return response.strip()


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":

    generator = ResponseGenerator()

    sample_memories = [

        {
            "memory": (
                "User likes cybersecurity"
            ),

            "final_score": 0.92
        },

        {
            "memory": (
                "User wants to become "
                "an AI engineer"
            ),

            "final_score": 0.88
        }
    ]

    response = generator.generate_response(

        user_message=(
            "Can you help me plan "
            "my AI learning journey?"
        ),

        retrieved_memories=sample_memories,

        emotion="motivated"
    )

    print("\n" + "=" * 60)

    print("ASSISTANT RESPONSE:")

    print("=" * 60)

    print(response)

    print("=" * 60)