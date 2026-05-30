# ============================================================
# anonymization.py
# Privacy & PII Anonymization Layer
# Removes or masks sensitive user information before storage
# ============================================================

from typing import Dict, Any, List
import re


# ============================================================
# ANONYMIZER
# ============================================================

class Anonymizer:

    def __init__(self):

        print("🚀 Initializing Anonymization Engine...")

        # simple regex-based patterns (extendable)
        self.patterns = {
            "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
            "phone": re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
            "ip": re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),
            "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
        }

        print("✅ Anonymizer Ready.")

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def anonymize_text(self, text: str) -> str:

        if not text:
            return text

        sanitized = text

        # EMAIL
        sanitized = self.patterns["email"].sub("[EMAIL]", sanitized)

        # PHONE
        sanitized = self.patterns["phone"].sub("[PHONE]", sanitized)

        # IP ADDRESS
        sanitized = self.patterns["ip"].sub("[IP_ADDRESS]", sanitized)

        # CREDIT CARD (very naive pattern)
        sanitized = self.patterns["credit_card"].sub("[CARD_NUMBER]", sanitized)

        return sanitized

    # ========================================================
    # ANONYMIZE MEMORY OBJECT
    # ========================================================

    def anonymize_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:

        if not isinstance(memory, dict):
            return memory

        cleaned = dict(memory)

        for key in ["memory", "text", "content"]:

            if key in cleaned and isinstance(cleaned[key], str):

                cleaned[key] = self.anonymize_text(cleaned[key])

        return cleaned

    # ========================================================
    # BATCH ANONYMIZATION
    # ========================================================

    def anonymize_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        return [self.anonymize_memory(item) for item in items]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    anon = Anonymizer()

    sample = {
        "memory": "User email is test@example.com and phone is 123-456-7890",
        "metadata": {}
    }

    print("\n=== BEFORE ===")
    print(sample)

    cleaned = anon.anonymize_memory(sample)

    print("\n=== AFTER ===")
    print(cleaned)