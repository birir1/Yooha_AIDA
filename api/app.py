# ============================================================
# app.py
# PRODUCTION MEMORY-AUGMENTED AI API SERVER (FIXED + WIRED + UI DASHBOARD)
# ============================================================

import os
import logging
import traceback

from flask import Flask, jsonify
from flask_cors import CORS

# ============================================================
# CONFIG
# ============================================================

PORT = int(os.getenv("PORT", 8000))

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ============================================================
# BLUEPRINTS
# ============================================================

from api.routes.chat_routes import chat_bp
from api.routes.memory_routes import memory_bp
from api.routes.admin_routes import admin_bp
from api.routes.analytics_routes import analytics_bp

# ============================================================
# UI ANALYTICS DASHBOARD (NEW)
# ============================================================

try:
    from api.analytics_dashboard import analytics_ui_bp
    analytics_dashboard_enabled = True
except Exception:
    logger.warning("⚠️ Analytics UI dashboard not found")
    analytics_ui_bp = None
    analytics_dashboard_enabled = False

# ============================================================
# OPTIONAL EMOTION ANALYTICS
# ============================================================

try:
    from api.routes.analytics_emotion_routes import emotion_analytics_bp
except Exception:
    logger.exception("❌ Emotion analytics blueprint failed to import")
    emotion_analytics_bp = None

# ============================================================
# CORE SERVICES (SAFE IMPORTS)
# ============================================================

try:
    from memory.memory_manager import MemoryManager
except Exception:
    logger.exception("MemoryManager import failed")
    MemoryManager = None

try:
    from api.services.llm_service import LLMService
except Exception:
    logger.exception("LLMService import failed")
    LLMService = None

try:
    from api.services.emotion_service import EmotionDetectionService
except Exception:
    logger.exception("Emotion service import failed")
    EmotionDetectionService = None

try:
    from retrieval.rag_pipeline import RAGPipeline
except Exception:
    logger.exception("RAGPipeline import failed")
    RAGPipeline = None

try:
    from retrieval.vector_store import VectorStore
except Exception:
    logger.exception("VectorStore import failed")
    VectorStore = None

# ============================================================
# APP INIT
# ============================================================

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config["JSON_SORT_KEYS"] = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# ============================================================
# SERVICE INIT HELPER
# ============================================================

def init_service(cls, name: str):
    if cls is None:
        logger.warning(f"⚠️ {name} not available")
        return None

    try:
        service = cls()
        logger.info(f"✅ {name} initialized")
        return service
    except Exception:
        logger.exception(f"❌ {name} init failed")
        return None

# ============================================================
# INITIALIZE SERVICES
# ============================================================

logger.info("🚀 Initializing Memory Manager...")
memory_manager = init_service(MemoryManager, "Memory Manager")

logger.info("🚀 Initializing LLM Service...")
llm_service = init_service(LLMService, "LLM Service")

logger.info("🚀 Initializing Emotion Detector...")
emotion_detector = init_service(EmotionDetectionService, "Emotion Detector")

logger.info("🚀 Initializing Vector Store...")
vector_store = None

try:
    if VectorStore is not None:
        vector_store = VectorStore()
        vector_store.load_from_file(
            "data/processed/embeddings/memory_embeddings.json"
        )
        logger.info("✅ Vector Store initialized")
except Exception:
    logger.exception("Vector Store failed")

logger.info("🚀 Initializing RAG Pipeline...")
rag_pipeline = init_service(RAGPipeline, "RAG Pipeline")

# ============================================================
# GLOBALS
# ============================================================

app.config.update({
    "MEMORY_MANAGER": memory_manager,
    "LLM_SERVICE": llm_service,
    "EMOTION_DETECTOR": emotion_detector,
    "VECTOR_STORE": vector_store,
    "RAG_PIPELINE": rag_pipeline
})

# ============================================================
# SERVICE STATUS
# ============================================================

def service_status(service):
    if service is None:
        return "offline"

    if hasattr(service, "health"):
        try:
            return "active" if service.health() else "offline"
        except Exception:
            return "offline"

    return "active"

# ============================================================
# HOME DASHBOARD
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Memory-Augmented AI Assistant</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #0b1220;
            color: white;
            margin: 0;
            padding: 0;
        }}
        .container {{
            padding: 30px;
            max-width: 1100px;
            margin: auto;
        }}
        .header {{
            background: #111827;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }}
        .card {{
            background: #1f2937;
            padding: 20px;
            border-radius: 12px;
        }}
        .btn {{
            display: inline-block;
            margin-top: 10px;
            padding: 10px 15px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }}
        .status {{
            color: #22c55e;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 20px;
            opacity: 0.6;
            text-align: center;
        }}
    </style>
</head>
<body>

<div class="container">

    <div class="header">
        <h1>🧠 Memory-Augmented AI Assistant</h1>
        <p>Backend Dashboard Interface</p>
        <p>Status: <span class="status">SERVER ONLINE</span></p>
        <p>Local URL: http://127.0.0.1:{PORT}</p>
    </div>

    <div class="grid">

        <div class="card">
            <h3>💬 Chat API</h3>
            <a class="btn" href="/api/chat/health">Open Chat API</a>
        </div>

        <div class="card">
            <h3>🧠 Memory API</h3>
            <a class="btn" href="/api/memory/health">Open Memory API</a>
        </div>

        <div class="card">
            <h3>📊 Analytics API</h3>
            <a class="btn" href="/api/analytics/">Open Analytics</a>
        </div>

        <div class="card">
            <h3>📈 Visual Dashboard</h3>
            <a class="btn" href="/api/analytics/dashboard">Open Charts</a>
        </div>

        <div class="card">
            <h3>⚙ Admin</h3>
            <a class="btn" href="/api/admin/">Open Admin</a>
        </div>

        <div class="card">
            <h3>🐞 Debug Memory</h3>
            <a class="btn" href="/api/debug/memory/stats">Open Debug</a>
        </div>

    </div>

    <div class="footer">
        Memory-Augmented AI Assistant Backend v2.0
    </div>

</div>

</body>
</html>
"""

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "application": "Memory-Augmented AI Assistant",
        "version": "4.1.0",
        "port": PORT,
        "services": {
            "memory_manager": service_status(app.config.get("MEMORY_MANAGER")),
            "llm_service": service_status(app.config.get("LLM_SERVICE")),
            "emotion_detector": service_status(app.config.get("EMOTION_DETECTOR")),
            "vector_store": service_status(app.config.get("VECTOR_STORE")),
            "rag_pipeline": service_status(app.config.get("RAG_PIPELINE"))
        }
    })

# ============================================================
# CHAT HEALTH
# ============================================================

@app.route("/api/chat/health", methods=["GET"])
def chat_health():
    return jsonify({
        "status": "ok",
        "llm_service": service_status(app.config.get("LLM_SERVICE")),
        "rag_pipeline": service_status(app.config.get("RAG_PIPELINE"))
    })

# ============================================================
# MEMORY STATS
# ============================================================

@app.route("/api/debug/memory/stats", methods=["GET"])
def memory_stats():
    try:
        memory_manager = app.config.get("MEMORY_MANAGER")

        if memory_manager is None:
            return jsonify({
                "status": "error",
                "message": "Memory manager unavailable"
            }), 500

        if hasattr(memory_manager, "get_memory_statistics"):
            stats = memory_manager.get_memory_statistics()
        else:
            stats = {"message": "Statistics unavailable"}

        return jsonify({
            "status": "ok",
            "stats": stats
        })

    except Exception as e:
        logger.exception("Memory stats failed")
        return jsonify({
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500

# ============================================================
# BLUEPRINT REGISTRATION
# ============================================================

logger.info("📦 Registering blueprints...")

try:
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(memory_bp, url_prefix="/api/memory")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")

    # UI DASHBOARD ROUTE
    if analytics_dashboard_enabled:
        app.register_blueprint(analytics_ui_bp, url_prefix="/api/analytics")

    if emotion_analytics_bp is not None:
        app.register_blueprint(emotion_analytics_bp, url_prefix="/api/analytics")

    logger.info("✅ Blueprints registered")

except Exception:
    logger.exception("❌ Blueprint registration failed")

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(_):
    return jsonify({"status": "error", "message": "Not found"}), 404

@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({"status": "error", "message": "Method not allowed"}), 405

@app.errorhandler(Exception)
def global_error(error):
    logger.exception("Unhandled exception")
    return jsonify({
        "status": "error",
        "message": str(error)
    }), 500

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("🚀 MEMORY AI SERVER ONLINE")
    print("=" * 70)
    print(f"Local URL  : http://127.0.0.1:{PORT}")
    print(f"Dashboard  : http://127.0.0.1:{PORT}/")
    print(f"Analytics  : http://127.0.0.1:{PORT}/api/analytics/dashboard")
    print("=" * 70)

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        threaded=True
    )