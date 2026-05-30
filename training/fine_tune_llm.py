# ============================================================
# fine_tune_llm.py (QLoRA SAFE VERSION - FIXES OOM COMPLETELY)
# ============================================================

import os
import json
from typing import List, Dict

import torch
from datasets import Dataset

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)

from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training
)

# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
DATA_PATH = "data/processed/llm_finetune_dataset_clean.jsonl"
OUTPUT_DIR = "models/llm/lora_finetuned"

MAX_SAMPLES = 50000
MAX_LENGTH = 512


# ============================================================
# LOAD DATA
# ============================================================

def load_training_data(path: str) -> List[Dict[str, str]]:
    data = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            msgs = obj.get("messages", [])

            text = ""
            for m in msgs:
                role = m["role"]
                content = m["content"]

                if role == "user":
                    text += f"User: {content}\n"
                elif role == "assistant":
                    text += f"Assistant: {content}\n"

            data.append({"text": text})

            if len(data) >= MAX_SAMPLES:
                break

    return data


# ============================================================
# TOKENIZE
# ============================================================

def tokenize(dataset, tokenizer):
    def fn(batch):
        out = tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH
        )
        out["labels"] = out["input_ids"].copy()
        return out

    return dataset.map(fn, batched=True, remove_columns=["text"])


# ============================================================
# TRAINER CLASS
# ============================================================

class LLMFineTuner:

    def __init__(self):

        print("🚀 Loading tokenizer...")

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        print("🚀 Loading 4-bit quantized model...")

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            quantization_config=bnb_config,
            device_map="auto"
        )

        model = prepare_model_for_kbit_training(model)

        # ====================================================
        # LoRA config (THIS FIXES EVERYTHING)
        # ====================================================

        lora_config = LoraConfig(
            r=8,
            lora_alpha=16,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )

        self.model = get_peft_model(model, lora_config)

        print("✅ Model loaded with LoRA.")

    # ========================================================
    # TRAIN
    # ========================================================

    def train(self, path: str, output_dir: str):

        print("🚀 Loading dataset...")

        data = load_training_data(path)
        dataset = Dataset.from_list(data)
        dataset = tokenize(dataset, self.tokenizer)

        dataset.set_format(type="torch")

        args = TrainingArguments(
            output_dir=output_dir,

            per_device_train_batch_size=1,
            gradient_accumulation_steps=16,

            learning_rate=2e-4,
            num_train_epochs=1,

            logging_steps=10,
            save_steps=200,

            fp16=True,

            report_to="none",
            remove_unused_columns=False
        )

        trainer = Trainer(
            model=self.model,
            args=args,
            train_dataset=dataset
        )

        print("🚀 Starting LoRA training (SAFE)...")

        trainer.train()

        print("💾 Saving LoRA adapters...")

        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        print("✅ DONE")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    trainer = LLMFineTuner()
    trainer.train(DATA_PATH, OUTPUT_DIR)
    
    