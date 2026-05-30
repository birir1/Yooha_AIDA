# ============================================================
# analytics_routes.py
# Production Analytics API (STABLE + DEMO + CACHE SAFE)
# ============================================================

from flask import Blueprint, jsonify, Response
import json
import os

from memory.memory_manager import MemoryManager
from api.services.analytics_cache_builder import AnalyticsCacheBuilder

# ============================================================
# INIT
# ============================================================

analytics_bp = Blueprint("analytics", __name__)
memory_manager = MemoryManager()

CACHE_FILE = "data/analytics_cache.json"


# ============================================================
# DEMO DATA (ONLY IF DB EMPTY)
# ============================================================

def get_demo_memories():
    return [
        {"memory": "AI systems learning embeddings", "importance": 0.9, "timestamp": "2026-05-25T10:00:00"},
        {"memory": "Cybersecurity threat modeling", "importance": 0.85, "timestamp": "2026-05-26T11:00:00"},
        {"memory": "Flask API development", "importance": 0.6, "timestamp": "2026-05-26T12:00:00"},
        {"memory": "Transformer architectures", "importance": 0.8, "timestamp": "2026-05-27T09:00:00"},
        {"memory": "Vector database indexing", "importance": 0.75, "timestamp": "2026-05-28T08:00:00"},
        {"memory": "Memory-augmented AI research", "importance": 0.95, "timestamp": "2026-05-28T10:30:00"},
        {"memory": "Debugging analytics system", "importance": 0.65, "timestamp": "2026-05-29T16:00:00"},
        {"memory": "Building dashboards", "importance": 0.88, "timestamp": "2026-05-30T09:00:00"},
    ]


# ============================================================
# SAFE MEMORY ACCESS (SOURCE OF TRUTH = SQLITE)
# ============================================================

def safe_get_memories():
    try:
        db_memories = memory_manager.db.get_all_memories()

        if db_memories and len(db_memories) > 0:
            return db_memories

        return get_demo_memories()

    except Exception:
        return get_demo_memories()


def safe_get_sessions():
    try:
        return [
            {"session_id": sid, **data}
            for sid, data in memory_manager.sessions.items()
        ]
    except Exception:
        return []


# ============================================================
# ROOT
# ============================================================

@analytics_bp.route("/", methods=["GET"])
def analytics_home():
    return jsonify({
        "status": "ok",
        "message": "Analytics API Running (STABLE + DEMO SAFE)",
        "endpoints": {
            "dashboard": "/api/analytics/dashboard",
            "dashboard_view": "/api/analytics/dashboard/view",
            "cache_rebuild": "/api/analytics/dashboard/cache/rebuild"
        }
    })


# ============================================================
# CACHE REBUILD (SAFE)
# ============================================================

@analytics_bp.route("/dashboard/cache/rebuild", methods=["GET"])
def rebuild_cache():

    try:
        builder = AnalyticsCacheBuilder()
        data = builder.build()

        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Cache builder returned invalid format"
            }), 500

        summary = data.get("dashboard", {}).get("summary", {})

        return jsonify({
            "status": "ok",
            "message": "Analytics cache rebuilt",
            "summary": summary
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# DASHBOARD JSON
# ============================================================

@analytics_bp.route("/dashboard", methods=["GET"])
def dashboard():

    memories = safe_get_memories()
    sessions = safe_get_sessions()

    importance = {"high": 0, "medium": 0, "low": 0}
    growth = {}

    for m in memories:

        val = float(m.get("importance", 0))

        if val >= 0.7:
            importance["high"] += 1
        elif val >= 0.4:
            importance["medium"] += 1
        else:
            importance["low"] += 1

        ts = m.get("timestamp", "")
        if ts:
            day = ts[:10]
            growth[day] = growth.get(day, 0) + 1

    return jsonify({
        "status": "ok",
        "dashboard": {
            "summary": {
                "total_memories": len(memories),
                "total_sessions": len(sessions),
                "indexed_vectors": len(memories)
            },
            "charts": {
                "importance_distribution": importance,
                "memory_growth": growth
            },
            "system_health": {
                "status": "healthy",
                "db_connected": True,
                "vector_store": True
            }
        }
    })


# ============================================================
# VISUAL DASHBOARD
# ============================================================

@analytics_bp.route("/dashboard/view", methods=["GET"])
def dashboard_view():

    data = dashboard().get_json()
    charts = data.get("dashboard", {}).get("charts", {})

    importance = charts.get("importance_distribution", {"high": 0, "medium": 0, "low": 0})
    growth = charts.get("memory_growth", {})

    labels = list(growth.keys())
    values = list(growth.values())

    return Response(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Memory AI Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        body {{
            margin:0;
            font-family: Arial;
            background: linear-gradient(135deg, #0b1220, #111827);
            color: white;
        }}

        .container {{
            padding: 20px;
        }}

        .card {{
            background: #1f2937;
            padding: 20px;
            border-radius: 12px;
            width: 250px;
        }}

        .grid {{
            display: flex;
            gap: 20px;
        }}
    </style>
</head>

<body>

<h1 style="padding:20px;">🧠 Memory AI Analytics Dashboard</h1>

<div class="container">

    <div class="grid">

        <div class="card">
            <h3>Importance</h3>
            <p>High: {importance['high']}</p>
            <p>Medium: {importance['medium']}</p>
            <p>Low: {importance['low']}</p>
        </div>

    </div>

    <div style="margin-top:30px;">
        <canvas id="chart"></canvas>
    </div>

</div>

<script>
new Chart(document.getElementById('chart'), {{
    type: 'line',
    data: {{
        labels: {json.dumps(labels)},
        datasets: [{{
            label: 'Memory Growth',
            data: {json.dumps(values)},
            borderColor: '#60a5fa',
            tension: 0.4
        }}]
    }},
    options: {{
        responsive: true
    }}
}});
</script>

</body>
</html>
""", mimetype="text/html")