# ============================================================
# privacy_filter.py
# Privacy Policy Enforcement Layer
# Blocks, flags, or sanitizes unsafe or sensitive content
# ============================================================

from typing import Dict, Any, List, Tuple
import re


# ============================================================
# PRIVACY FILTER
# ============================================================

class PrivacyFilter:

    def __init__(self):

        print("🚀 Initializing Privacy Filter...")

        # categories of sensitive patterns
        self.rules = {
            "pii": [
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",  # email
                r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",               # phone
                r"\b\d{1,3}(?:\.\d{1,3}){3}\b"                      # IP
            ],
            "financial": [
                r"\b(?:\d[ -]*?){13,16}\b"  # credit card-like pattern
            ],
            "secrets": [
                r"password\s*[:=]\s*\S+",
                r"api[_-]?key\s*[:=]\s*\S+",
                r"secret\s*[:=]\s*\S+"
            ]
        }

        print("✅ Privacy Filter Ready.")

    # ========================================================
    # SCAN TEXT
    # ========================================================

    def scan(self, text: str) -> Dict[str, Any]:

        if not text:
            return {
                "safe": True,
                "flags": []
            }

        flags = []

        for category, patterns in self.rules.items():

            for pattern in patterns:

                if re.search(pattern, text, re.IGNORECASE):

                    flags.append(category)
                    break

        return {
            "safe": len(flags) == 0,
            "flags": list(set(flags))
        }

    # ========================================================
    # SANITIZE TEXT
    # ========================================================

    def sanitize(self, text: str) -> str:

        if not text:
            return text

        cleaned = text

        # replace PII
        for pattern in self.rules["pii"]:
            cleaned = re.sub(pattern, "[REDACTED_PII]", cleaned)

        # replace financial info
        for pattern in self.rules["financial"]:
            cleaned = re.sub(pattern, "[REDACTED_FINANCIAL]", cleaned)

        # replace secrets
        for pattern in self.rules["secrets"]:
            cleaned = re.sub(pattern, "[REDACTED_SECRET]", cleaned, flags=re.IGNORECASE)

        return cleaned

    # ========================================================
    # PROCESS MEMORY OBJECT
    # ========================================================

    def process_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:

        if not isinstance(memory, dict):
            return memory

        result = dict(memory)

        for key in ["memory", "text", "content"]:

            if key in result and isinstance(result[key], str):

                scan_result = self.scan(result[key])

                result[key] = self.sanitize(result[key])

                result["privacy_flags"] = scan_result["flags"]
                result["is_safe"] = scan_result["safe"]

        return result

    # ========================================================
    # BATCH PROCESSING
    # ========================================================

    def process_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        return [self.process_memory(item) for item in items]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    pf = PrivacyFilter()

    sample = {
        "memory": "My email is test@example.com and API_KEY=12345",
        "metadata": {}
    }

    print("\n=== BEFORE ===")
    print(sample)

    cleaned = pf.process_memory(sample)

    print("\n=== AFTER ===")
    print(cleaned)