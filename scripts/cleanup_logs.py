# ============================================================
# cleanup_logs.py
# Log Cleanup Utility Script
# Removes old logs and optimizes storage for monitoring system
# ============================================================

import os
import time
from datetime import datetime, timedelta


# ============================================================
# CONFIGURATION
# ============================================================

LOG_DIRECTORIES = [
    "monitoring/logging/system_logs",
    "monitoring/logging/interaction_logs"
]

RETENTION_DAYS = 7


# ============================================================
# CLEANUP UTILITY
# ============================================================

class LogCleaner:

    def __init__(self, retention_days: int = RETENTION_DAYS):

        print("🚀 Initializing Log Cleaner...")

        self.retention_days = retention_days
        self.cutoff_time = time.time() - (retention_days * 86400)

        print(f"🧹 Retention policy: {retention_days} days")

    # ========================================================
    # CLEAN DIRECTORY
    # ========================================================

    def clean_directory(self, path: str) -> dict:

        removed_files = 0
        freed_space = 0

        if not os.path.exists(path):
            return {
                "path": path,
                "status": "not_found",
                "removed_files": 0,
                "freed_space": 0
            }

        for root, _, files in os.walk(path):

            for file in files:

                file_path = os.path.join(root, file)

                try:

                    file_stat = os.stat(file_path)

                    if file_stat.st_mtime < self.cutoff_time:

                        size = file_stat.st_size

                        os.remove(file_path)

                        removed_files += 1
                        freed_space += size

                except Exception as e:

                    print(f"[WARN] Failed to remove {file_path}: {e}")

        return {
            "path": path,
            "status": "cleaned",
            "removed_files": removed_files,
            "freed_space_mb": round(freed_space / (1024 * 1024), 2)
        }

    # ========================================================
    # RUN CLEANUP
    # ========================================================

    def run(self) -> dict:

        results = []

        print("\n🧹 Starting log cleanup...\n")

        for directory in LOG_DIRECTORIES:

            result = self.clean_directory(directory)
            results.append(result)

            print(f"✔ {directory} -> {result['removed_files']} files removed")

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "retention_days": self.retention_days,
            "results": results
        }

        print("\n✅ Cleanup completed.")

        return summary


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    cleaner = LogCleaner(retention_days=7)

    report = cleaner.run()

    print("\n=== CLEANUP REPORT ===")
    print(report)