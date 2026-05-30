# ============================================================
# test_full_pipeline.py
# Full System Pipeline Test (Robust + Auto-Failover)
# ============================================================

import requests
import time
import uuid
import os
from typing import Dict, Any, Tuple


# ============================================================
# CONFIG
# ============================================================

BASE_URL = os.getenv("CHAT_API_URL", "http://127.0.0.1:8000/api/chat/")

TIMEOUT = 20


# ============================================================
# SEND MESSAGE
# ============================================================

def send_message(message: str, session_id: str) -> Tuple[Dict[str, Any], float]:

    payload = {
        "message": message,
        "session_id": session_id,
        "user_id": "test_user",
        "top_k": 5
    }

    start = time.time()

    try:
        response = requests.post(
            BASE_URL,
            json=payload,
            timeout=TIMEOUT
        )

        latency = round(time.time() - start, 3)

        response.raise_for_status()

        return response.json(), latency

    except requests.exceptions.ConnectionError:

        raise RuntimeError(
            f"❌ Cannot connect to API at {BASE_URL}\n"
            f"Make sure your Flask server is running:\n"
            f"python api/app.py OR flask run --port 8000"
        )

    except Exception as e:

        latency = round(time.time() - start, 3)

        return {
            "error": str(e),
            "raw": None
        }, latency


# ============================================================
# RUN TESTS
# ============================================================

def run_tests():

    print("\n🚀 STARTING FULL PIPELINE TEST\n")

    session_id = str(uuid.uuid4())

    test_cases = [
        "Hi there",
        "I want to learn AI",
        "Tell me about cybersecurity",
        "What is machine learning?",
        "Do you remember what I like?"
    ]

    results = []

    for i, test in enumerate(test_cases, 1):

        print(f"\n🧪 TEST {i}/{len(test_cases)}")
        print(f"INPUT: {test}")

        try:
            result, latency = send_message(test, session_id)

            print(f"LATENCY: {latency}s")

            if "error" in result:
                print("❌ ERROR RESPONSE")
                print(result["error"])
            else:
                print("✅ RESPONSE:")
                print(result.get("response", "No response field"))

                print(f"MEMORIES: {result.get('memory_count', 0)}")

            results.append(result)

        except RuntimeError as e:
            print(str(e))
            print("\n🛑 STOPPING TEST (server not running)")
            return

        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n\n==============================")
    print("📊 FINAL TEST SUMMARY")
    print("==============================")

    print(f"Total tests: {len(results)}")

    success = sum(1 for r in results if "error" not in r)

    print(f"Successful: {success}")
    print(f"Failed: {len(results) - success}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_tests()