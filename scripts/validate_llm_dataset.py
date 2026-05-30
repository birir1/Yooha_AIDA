import json

INPUT_PATH = "data/processed/llm_finetune_dataset.jsonl"
OUTPUT_PATH = "data/processed/llm_finetune_dataset_clean.jsonl"


def is_valid_message(msg):
    if not isinstance(msg, dict):
        return False

    if "messages" not in msg:
        return False

    messages = msg["messages"]

    if not isinstance(messages, list):
        return False

    for m in messages:
        if not isinstance(m, dict):
            return False

        if "role" not in m or "content" not in m:
            return False

        if not isinstance(m["content"], str):
            return False

        if len(m["content"].strip()) == 0:
            return False

    return True


def clean_dataset():
    print("🚀 Validating dataset...")

    valid = []
    total = 0
    removed = 0

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            total += 1

            try:
                obj = json.loads(line)

                if is_valid_message(obj):
                    valid.append(obj)
                else:
                    removed += 1

            except Exception:
                removed += 1

    print(f"Total: {total}")
    print(f"Valid: {len(valid)}")
    print(f"Removed: {removed}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for v in valid:
            f.write(json.dumps(v) + "\n")

    print(f"Saved CLEAN dataset → {OUTPUT_PATH}")
    print("Done ✅")


if __name__ == "__main__":
    clean_dataset()