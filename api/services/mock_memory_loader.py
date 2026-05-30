import json
import os

DATA_PATH = "data/sample_memory_dataset.json"


def load_mock_memories():
    if not os.path.exists(DATA_PATH):
        return []

    with open(DATA_PATH, "r") as f:
        return json.load(f)