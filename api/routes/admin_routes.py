# ============================================================
# admin_routes.py
# Production Admin Control API
# ============================================================

from flask import Blueprint, jsonify

from memory.memory_manager import MemoryManager


# ============================================================
# BLUEPRINT
# ============================================================

admin_bp = Blueprint("admin", __name__)

# Shared memory manager
memory_manager = MemoryManager()


# ============================================================
# ADMIN ROOT
# ============================================================

@admin_bp.route("/", methods=["GET"])
def admin_home():

    return jsonify({
        "status": "ok",
        "message": "Admin Control API Running",
        "available_endpoints": {
            "health": "/api/admin/health",
            "system_stats": "/api/admin/system/stats",
            "memory_stats": "/api/admin/memory/stats",
            "memory_decay": "/api/admin/memory/decay",
            "rebuild_index": "/api/admin/index/rebuild",
            "retriever_status": "/api/admin/retriever/status",
            "clear_sessions": "/api/admin/session/clear",
            "active_sessions": "/api/admin/session/active"
        }
    }), 200


# ============================================================
# SYSTEM HEALTH CHECK
# ============================================================

@admin_bp.route("/health", methods=["GET"])
def system_health():

    try:

        retriever_loaded = (
            hasattr(memory_manager, "retriever")
        )

        db_connected = (
            hasattr(memory_manager, "db")
        )

        summarizer_loaded = (
            hasattr(memory_manager, "summarizer")
        )

        return jsonify({
            "status": "ok",
            "service": "memory-ai-system",
            "components": {
                "memory_manager": "active",
                "retriever": (
                    "active" if retriever_loaded else "inactive"
                ),
                "database": (
                    "connected" if db_connected else "disconnected"
                ),
                "summarizer": (
                    "loaded" if summarizer_loaded else "disabled"
                )
            }
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# SYSTEM STATS
# ============================================================

@admin_bp.route("/system/stats", methods=["GET"])
def system_stats():

    try:

        db_stats = memory_manager.db.get_stats()

        retriever_memories = len(
            memory_manager.retriever.memories
        )

        active_sessions = len(
            memory_manager.sessions
        )

        return jsonify({
            "status": "ok",
            "system": {
                "active_sessions": active_sessions,
                "retriever_memories": retriever_memories,
                "database_stats": db_stats
            }
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# MEMORY STATS
# ============================================================

@admin_bp.route("/memory/stats", methods=["GET"])
def memory_stats():

    try:

        stats = memory_manager.db.get_stats()

        forgetting_stats = (
            memory_manager.forgetting.statistics()
        )

        return jsonify({
            "status": "ok",
            "database": stats,
            "memory_statistics": forgetting_stats
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# RUN MEMORY DECAY
# ============================================================

@admin_bp.route("/memory/decay", methods=["POST"])
def force_decay():

    try:

        result = (
            memory_manager.apply_forgetting()
        )

        return jsonify({
            "status": "success",
            "message": "Memory forgetting cycle completed",
            "result": result
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# RETRIEVER STATUS
# ============================================================

@admin_bp.route("/retriever/status", methods=["GET"])
def retriever_status():

    try:

        retriever = memory_manager.retriever

        return jsonify({
            "status": "ok",
            "retriever": {
                "embedding_dimension": retriever.dim,
                "indexed_memories": len(retriever.memories),
                "metadata_entries": len(retriever.metadata),
                "cache_enabled": retriever.use_cache
            }
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# REBUILD VECTOR INDEX
# ============================================================

@admin_bp.route("/index/rebuild", methods=["POST"])
def rebuild_index():

    try:

        memory_manager.retriever._load_or_build_index()

        return jsonify({
            "status": "success",
            "message": "FAISS index rebuilt successfully",
            "indexed_memories": len(
                memory_manager.retriever.memories
            )
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# ACTIVE SESSIONS
# ============================================================

@admin_bp.route("/session/active", methods=["GET"])
def active_sessions():

    try:

        return jsonify({
            "status": "ok",
            "active_sessions": memory_manager.sessions,
            "count": len(memory_manager.sessions)
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# CLEAR SESSION CACHE
# ============================================================

@admin_bp.route("/session/clear", methods=["POST"])
def clear_sessions():

    try:

        cleared = len(memory_manager.sessions)

        memory_manager.sessions.clear()

        return jsonify({
            "status": "success",
            "message": "All active sessions cleared",
            "cleared_sessions": cleared
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500