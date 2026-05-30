# ============================================================
# encryption.py
# Lightweight Encryption Layer for Sensitive Memory Storage
# NOTE: Production systems should use proper key management (KMS)
# ============================================================

from typing import Optional
import base64
import hashlib
import os


# ============================================================
# ENCRYPTION ENGINE
# ============================================================

class SimpleEncryption:

    def __init__(self, secret_key: Optional[str] = None):

        print("🚀 Initializing Encryption Engine...")

        # In production, load from env or secure vault
        self.secret_key = secret_key or os.getenv("MEMORY_SECRET_KEY", "default_insecure_key")

        # derive fixed-length key
        self.derived_key = hashlib.sha256(self.secret_key.encode()).digest()

        print("✅ Encryption Engine Ready.")

    # ========================================================
    # XOR ENCRYPTION (SYMMETRIC, SIMPLE DEMO)
    # ========================================================

    def _xor(self, data: bytes) -> bytes:

        key = self.derived_key
        key_len = len(key)

        return bytes(
            b ^ key[i % key_len]
            for i, b in enumerate(data)
        )

    # ========================================================
    # ENCRYPT
    # ========================================================

    def encrypt(self, plaintext: str) -> str:

        if not plaintext:
            return plaintext

        raw = plaintext.encode("utf-8")

        encrypted_bytes = self._xor(raw)

        encoded = base64.b64encode(encrypted_bytes).decode("utf-8")

        return encoded

    # ========================================================
    # DECRYPT
    # ========================================================

    def decrypt(self, ciphertext: str) -> str:

        if not ciphertext:
            return ciphertext

        try:

            decoded = base64.b64decode(ciphertext.encode("utf-8"))

            decrypted_bytes = self._xor(decoded)

            return decrypted_bytes.decode("utf-8")

        except Exception:
            return ""


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    enc = SimpleEncryption("my_secret_key")

    message = "User likes AI and cybersecurity"

    encrypted = enc.encrypt(message)
    decrypted = enc.decrypt(encrypted)

    print("\n=== ENCRYPTION TEST ===")
    print("Original:", message)
    print("Encrypted:", encrypted)
    print("Decrypted:", decrypted)