import json
import re

INPUT_PATH = "data/processed/llm_finetune_dataset_clean.jsonl"
OUTPUT_PATH = "data/processed/llm_finetune_dataset_final.jsonl"


# ============================================================
# QUALITY RULES (CRITICAL FOR LLM TRAINING)
# ============================================================

def is_bad_text(text: str) -> bool:
    text = text.strip()

    if len(text) < 3:
        return True

    if text in ["0", "1", "2", "true", "false"]:
        return True

    if re.fullmatch(r"\d+", text):  # pure numbers
        return True

    if text.lower() in ["none", "null", "undefined"]:
        return True

    return False


def is_good_sample(sample: dict) -> bool:
    try:
        messages = sample["messages"]

        if len(messages) < 2:
            return False

        user = messages[1]["content"]
        assistant = messages[2]["content"]

        if not isinstance(user, str) or not isinstance(assistant, str):
            return False

        if is_bad_text(user) or is_bad_text(assistant):
            return False

        # remove mirror pairs like 0→0 or 1→1
        if user.strip() == assistant.strip():
            return False

        return True

    except Exception:
        return False


# ============================================================
# FILTER PIPELINE
# ============================================================

def run_filter():
    print("🚀 Running QUALITY filter on dataset...")

    total = 0
    kept = 0

    with open(INPUT_PATH, "r", encoding="utf-8") as f, \
         open(OUTPUT_PATH, "w", encoding="utf-8") as out:

        for line in f:
            total += 1

            try:
                obj = json.loads(line)

                if is_good_sample(obj):
                    out.write(json.dumps(obj) + "\n")
                    kept += 1

            except Exception:
                continue

    print(f"Total: {total}")
    print(f"Kept: {kept}")
    print(f"Removed: {total - kept}")
    print("Done ✅")


if __name__ == "__main__":
    run_filter()