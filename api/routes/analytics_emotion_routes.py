# ============================================================
# analytics_emotion_routes.py
# EMOTION ANALYTICS ENGINE (TIME-SERIES + DASHBOARD READY)
# ============================================================

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from collections import defaultdict
import logging
import json

logger = logging.getLogger(__name__)

emotion_analytics_bp = Blueprint("emotion_analytics", __name__)


# ============================================================
# SAFE PARSER (handles stored memory payload strings)
# ============================================================

def try_parse_memory(memory):
    """
    Converts stored memory string/dict into usable structure
    """
    try:
        if isinstance(memory, dict):
            return memory

        if isinstance(memory, str):
            # try JSON parsing
            try:
                return json.loads(memory)
            except Exception:
                return None

        return None
    except Exception:
        return None


# ============================================================
# EXTRACT EMOTION EVENTS
# ============================================================

def extract_emotion_events(memories):
    """
    Converts raw memory logs into structured emotion timeline
    """
    events = []

    for m in memories or []:
        parsed = try_parse_memory(m)

        if not parsed:
            continue

        emotion_event = parsed.get("emotion_event")

        if emotion_event:
            events.append({
                "session_id": parsed.get("session_id"),
                "user_id": parsed.get("user_id"),
                "emotion": emotion_event.get("emotion", "neutral"),
                "timestamp": emotion_event.get("timestamp")
            })

    return events


# ============================================================
# SESSION EMOTION TIMELINE
# ============================================================

@emotion_analytics_bp.route("/emotions/session/<session_id>", methods=["GET"])
def session_emotion_timeline(session_id):
    try:
        memory_manager = current_app.config.get("MEMORY_MANAGER")

        if not memory_manager:
            return jsonify({"status": "error", "message": "Memory system unavailable"}), 500

        # pull all memories for session
        if hasattr(memory_manager, "retrieve_by_session"):
            memories = memory_manager.retrieve_by_session(session_id)
        elif hasattr(memory_manager, "retrieve_memory"):
            memories = memory_manager.retrieve_memory(session_id=session_id, query="", top_k=1000)
        else:
            memories = []

        events = extract_emotion_events(memories)

        # sort by time
        events.sort(key=lambda x: x.get("timestamp", ""))

        # format for graphs
        timeline = [
            {
                "t": i,
                "emotion": e["emotion"],
                "timestamp": e["timestamp"]
            }
            for i, e in enumerate(events)
        ]

        return jsonify({
            "status": "success",
            "session_id": session_id,
            "count": len(timeline),
            "timeline": timeline
        })

    except Exception as e:
        logger.exception("Session emotion timeline failed")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# GLOBAL EMOTION TRENDS
# ============================================================

@emotion_analytics_bp.route("/emotions/global", methods=["GET"])
def global_emotion_trends():
    try:
        memory_manager = current_app.config.get("MEMORY_MANAGER")

        if not memory_manager:
            return jsonify({"status": "error"}), 500

        # get all memories (depends on implementation)
        if hasattr(memory_manager, "get_all_memories"):
            memories = memory_manager.get_all_memories()
        else:
            return jsonify({
                "status": "error",
                "message": "Global retrieval not supported"
            }), 501

        events = extract_emotion_events(memories)

        # aggregate emotions
        counts = defaultdict(int)

        for e in events:
            counts[e["emotion"]] += 1

        total = sum(counts.values()) or 1

        distribution = {
            k: {
                "count": v,
                "percentage": round((v / total) * 100, 2)
            }
            for k, v in counts.items()
        }

        return jsonify({
            "status": "success",
            "total_events": total,
            "distribution": distribution
        })

    except Exception as e:
        logger.exception("Global emotion trends failed")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# EMOTION HEATMAP (SESSION OVERVIEW)
# ============================================================

@emotion_analytics_bp.route("/emotions/heatmap", methods=["GET"])
def emotion_heatmap():
    """
    Groups emotions per session for visualization
    """
    try:
        memory_manager = current_app.config.get("MEMORY_MANAGER")

        if not memory_manager:
            return jsonify({"status": "error"}), 500

        if hasattr(memory_manager, "get_all_memories"):
            memories = memory_manager.get_all_memories()
        else:
            return jsonify({"status": "error"}), 501

        events = extract_emotion_events(memories)

        heatmap = defaultdict(lambda: defaultdict(int))

        for e in events:
            session = e["session_id"]
            emotion = e["emotion"]
            heatmap[session][emotion] += 1

        formatted = {
            session: dict(emotions)
            for session, emotions in heatmap.items()
        }

        return jsonify({
            "status": "success",
            "heatmap": formatted
        })

    except Exception as e:
        logger.exception("Emotion heatmap failed")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# HEALTH
# ============================================================

@emotion_analytics_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "emotion_analytics",
        "features": [
            "session_timeline",
            "global_trends",
            "emotion_heatmap"
        ]
    })