# ============================================================
# memory_routes.py
# Production Memory API Routes
# ============================================================

from flask import Blueprint, request, jsonify

from memory.memory_manager import MemoryManager


# ============================================================
# BLUEPRINT
# ============================================================

memory_bp = Blueprint("memory", __name__)

# Shared memory manager instance
memory_manager = MemoryManager()


# ============================================================
# API ROOT
# ============================================================

@memory_bp.route("/", methods=["GET"])
def memory_home():

    return jsonify({
        "status": "ok",
        "message": "Memory API Running",
        "available_endpoints": {
            "stats": "/api/memory/stats",
            "retrieve": "/api/memory/retrieve",
            "session_history": "/api/memory/session/<session_id>",
            "session_summary": "/api/memory/session/<session_id>/summary",
            "session_memories": "/api/memory/session/<session_id>/memories",
            "delete_session": "/api/memory/session/<session_id>",
            "forgetting": "/api/memory/forgetting/run"
        }
    }), 200


# ============================================================
# MEMORY STATS
# ============================================================

@memory_bp.route("/stats", methods=["GET"])
def get_memory_stats():

    try:

        stats = memory_manager.db.get_stats()

        return jsonify({
            "status": "ok",
            "stats": stats
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# GET SESSION HISTORY
# ============================================================

@memory_bp.route("/session/<session_id>", methods=["GET"])
def get_session_history(session_id):

    try:

        messages = memory_manager.get_history(session_id)

        return jsonify({
            "status": "ok",
            "session_id": session_id,
            "message_count": len(messages),
            "messages": messages
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# GET SESSION MEMORIES
# ============================================================

@memory_bp.route("/session/<session_id>/memories", methods=["GET"])
def get_session_memories(session_id):

    try:

        memories = memory_manager.db.get_memories(session_id)

        return jsonify({
            "status": "ok",
            "session_id": session_id,
            "memory_count": len(memories),
            "memories": memories
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# SESSION SUMMARY
# ============================================================

@memory_bp.route("/session/<session_id>/summary", methods=["GET"])
def summarize_session(session_id):

    try:

        summary = memory_manager.summarize_session(session_id)

        return jsonify({
            "status": "ok",
            "session_id": session_id,
            "summary": summary
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# SEMANTIC MEMORY RETRIEVAL
# ============================================================

@memory_bp.route("/retrieve", methods=["POST"])
def retrieve_memory():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "JSON body required"
            }), 400

        query = data.get("query", "").strip()
        top_k = int(data.get("top_k", 5))

        if not query:
            return jsonify({
                "status": "error",
                "message": "query field required"
            }), 400

        results = memory_manager.retrieve_memory(
            session_id=data.get("session_id", ""),
            query=query,
            top_k=top_k
        )

        return jsonify({
            "status": "ok",
            "query": query,
            "top_k": top_k,
            "result_count": len(results),
            "results": results
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# RUN FORGETTING PIPELINE
# ============================================================

@memory_bp.route("/forgetting/run", methods=["POST"])
def run_forgetting():

    try:

        result = memory_manager.apply_forgetting()

        return jsonify({
            "status": "ok",
            "result": result
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# DELETE SESSION
# ============================================================

@memory_bp.route("/session/<session_id>", methods=["DELETE"])
def delete_session(session_id):

    try:

        deleted = memory_manager.delete_session(session_id)

        return jsonify({
            "status": "ok",
            "deleted": deleted,
            "session_id": session_id
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@memory_bp.route("/health", methods=["GET"])
def memory_health():

    return jsonify({
        "status": "ok",
        "service": "memory_api"
    }), 200