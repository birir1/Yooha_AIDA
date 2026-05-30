# ============================================================
# secure_memory_storage.py
# Secure Storage Layer for Memory-Augmented AI System
# Combines encryption + anonymization + privacy filtering
# ============================================================

from typing import Dict, Any, List, Optional
import json
import os
import time

from security.encryption import SimpleEncryption
from security.anonymization import Anonymizer
from security.privacy_filter import PrivacyFilter


# ============================================================
# SECURE MEMORY STORAGE
# ============================================================

class SecureMemoryStorage:

    def __init__(self, storage_path: Optional[str] = None):

        print("🚀 Initializing Secure Memory Storage...")

        self.storage_path = storage_path or "data/secure_memory.json"

        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        # security components
        self.encryption = SimpleEncryption()
        self.anonymizer = Anonymizer()
        self.privacy_filter = PrivacyFilter()

        # in-memory buffer
        self.buffer: List[Dict[str, Any]] = []

        print("✅ Secure Memory Storage Ready.")

    # ========================================================
    # STORE MEMORY SECURELY
    # ========================================================

    def store(self, memory: Dict[str, Any]) -> bool:

        if not isinstance(memory, dict):
            return False

        # ----------------------------------------------------
        # STEP 1: Privacy scan + sanitize
        # ----------------------------------------------------

        memory = self.privacy_filter.process_memory(memory)

        # ----------------------------------------------------
        # STEP 2: Anonymize content
        # ----------------------------------------------------

        memory = self.anonymizer.anonymize_memory(memory)

        # ----------------------------------------------------
        # STEP 3: Encrypt sensitive fields
        # ----------------------------------------------------

        memory = self._encrypt_memory_fields(memory)

        # ----------------------------------------------------
        # STEP 4: Add metadata
        # ----------------------------------------------------

        memory["stored_at"] = time.time()

        self.buffer.append(memory)

        # persist to disk
        self._flush()

        return True

    # ========================================================
    # RETRIEVE MEMORIES (DECRYPTED)
    # ========================================================

    def retrieve_all(self) -> List[Dict[str, Any]]:

        results = []

        for item in self.buffer:

            decrypted = self._decrypt_memory_fields(item)

            results.append(decrypted)

        return results

    # ========================================================
    # FIELD ENCRYPTION
    # ========================================================

    def _encrypt_memory_fields(self, memory: Dict[str, Any]) -> Dict[str, Any]:

        encrypted = dict(memory)

        for key in ["memory", "text", "content"]:

            if key in encrypted and isinstance(encrypted[key], str):

                encrypted[key] = self.encryption.encrypt(encrypted[key])

        return encrypted

    # ========================================================
    # FIELD DECRYPTION
    # ========================================================

    def _decrypt_memory_fields(self, memory: Dict[str, Any]) -> Dict[str, Any]:

        decrypted = dict(memory)

        for key in ["memory", "text", "content"]:

            if key in decrypted and isinstance(decrypted[key], str):

                decrypted[key] = self.encryption.decrypt(decrypted[key])

        return decrypted

    # ========================================================
    # FLUSH TO DISK
    # ========================================================

    def _flush(self):

        try:

            with open(self.storage_path, "w", encoding="utf-8") as f:

                json.dump(self.buffer, f, indent=2)

        except Exception as e:

            print(f"[ERROR] Failed to flush secure storage: {e}")

    # ========================================================
    # LOAD FROM DISK
    # ========================================================

    def load(self):

        if not os.path.exists(self.storage_path):
            return

        try:

            with open(self.storage_path, "r", encoding="utf-8") as f:

                self.buffer = json.load(f)

        except Exception as e:

            print(f"[ERROR] Failed to load secure storage: {e}")


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    storage = SecureMemoryStorage()

    storage.store({
        "memory": "User email is test@example.com and likes AI",
        "metadata": {"source": "test"}
    })

    print("\n=== STORED (RAW BUFFER) ===")
    print(storage.buffer)

    print("\n=== DECRYPTED RETRIEVAL ===")
    print(storage.retrieve_all())