# ============================================================
# access_control.py
# Basic Access Control Layer for Memory-Augmented AI System
# Handles user roles, permissions, and session validation
# ============================================================

from typing import Dict, List, Optional
import uuid
from datetime import datetime, timedelta


# ============================================================
# ACCESS CONTROL MANAGER
# ============================================================

class AccessControl:

    def __init__(self):

        print("🚀 Initializing Access Control System...")

        # in-memory session store (replace with Redis in production)
        self.sessions: Dict[str, Dict] = {}

        # role-based permissions
        self.roles = {
            "admin": ["read", "write", "delete", "manage"],
            "user": ["read", "write"],
            "guest": ["read"]
        }

        print("✅ Access Control Ready.")

    # ========================================================
    # SESSION CREATION
    # ========================================================

    def create_session(
        self,
        user_id: str,
        role: str = "user",
        ttl_minutes: int = 60
    ) -> str:

        if role not in self.roles:
            raise ValueError(f"Invalid role: {role}")

        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            "user_id": user_id,
            "role": role,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=ttl_minutes)
        }

        print(f"🔐 Session created for {user_id} ({role})")

        return session_id

    # ========================================================
    # VALIDATE SESSION
    # ========================================================

    def validate_session(self, session_id: str) -> bool:

        session = self.sessions.get(session_id)

        if not session:
            return False

        if datetime.utcnow() > session["expires_at"]:
            self.sessions.pop(session_id, None)
            return False

        return True

    # ========================================================
    # CHECK PERMISSION
    # ========================================================

    def check_permission(
        self,
        session_id: str,
        action: str
    ) -> bool:

        session = self.sessions.get(session_id)

        if not session:
            return False

        role = session.get("role", "guest")

        return action in self.roles.get(role, [])

    # ========================================================
    # GET USER INFO
    # ========================================================

    def get_user(self, session_id: str) -> Optional[Dict]:

        return self.sessions.get(session_id)

    # ========================================================
    # DELETE SESSION
    # ========================================================

    def revoke_session(self, session_id: str) -> bool:

        if session_id in self.sessions:

            self.sessions.pop(session_id)

            print(f"🗑️ Session revoked: {session_id}")

            return True

        return False

    # ========================================================
    # CLEAN EXPIRED SESSIONS
    # ========================================================

    def cleanup_sessions(self):

        now = datetime.utcnow()

        expired = [
            sid for sid, s in self.sessions.items()
            if now > s["expires_at"]
        ]

        for sid in expired:
            self.sessions.pop(sid, None)

        print(f"🧹 Cleaned {len(expired)} expired sessions")

        return len(expired)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    ac = AccessControl()

    session = ac.create_session("user_001", role="user")

    print("Valid:", ac.validate_session(session))
    print("Can read:", ac.check_permission(session, "read"))
    print("Can delete:", ac.check_permission(session, "delete"))

    ac.cleanup_sessions()