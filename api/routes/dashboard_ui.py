from flask import Blueprint, jsonify, render_template_string, current_app

dashboard_bp = Blueprint("dashboard", __name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AIDA Backend Dashboard</title>
    <style>
        body {
            font-family: Arial;
            background: #0f172a;
            color: white;
            margin: 0;
            padding: 0;
        }

        .header {
            padding: 20px;
            background: #111827;
            font-size: 22px;
            font-weight: bold;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            padding: 20px;
        }

        .card {
            background: #1f2937;
            padding: 20px;
            border-radius: 12px;
        }

        .btn {
            display: inline-block;
            margin-top: 10px;
            padding: 8px 12px;
            background: #2563eb;
            color: white;
            border-radius: 8px;
            text-decoration: none;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #9ca3af;
        }

        .status-box {
            margin: 20px;
            padding: 15px;
            background: #0b1220;
            border-radius: 10px;
            border: 1px solid #1f2937;
        }
    </style>
</head>

<body>

<div class="header">
🧠 Memory-Augmented AI Assistant Backend
</div>

<div class="status-box">
    <p>🔌 System Status: <b>ONLINE</b></p>
    <p>🧠 Memory: ACTIVE</p>
    <p>📊 RAG Pipeline: ENABLED</p>
    <p>📡 Analytics: READY</p>
</div>

<div class="grid">

    <div class="card">
        <h3>💬 Chat API</h3>
        <p>Test conversational AI endpoint</p>
        <a class="btn" href="/api/chat/">Open Chat API</a>
    </div>

    <div class="card">
        <h3>🧠 Memory API</h3>
        <p>View stored memories & retrieval system</p>
        <a class="btn" href="/api/memory">Open Memory API</a>
    </div>

    <div class="card">
        <h3>📊 Analytics</h3>
        <p>System usage and memory stats</p>
        <a class="btn" href="/api/analytics">Open Analytics API</a>
    </div>

    <div class="card">
        <h3>📈 Emotion Dashboard</h3>
        <p>View session-based emotion graphs</p>
        <a class="btn" href="/dashboard/analytics">Open Emotion Dashboard</a>
    </div>

    <div class="card">
        <h3>⚙ Admin</h3>
        <p>System configuration & controls</p>
        <a class="btn" href="/api/admin">Open Admin</a>
    </div>

    <div class="card">
        <h3>❤️ Health</h3>
        <p>Backend service status</p>
        <a class="btn" href="/api/chat/health">Check Health</a>
    </div>

    <div class="card">
        <h3>🐞 Debug</h3>
        <p>Inspect memory + RAG pipeline</p>
        <a class="btn" href="/api/debug/memory/stats">Open Debug</a>
    </div>

</div>

<div class="footer">
Version 2.1 • AIDA Backend System
</div>

</body>
</html>
"""


@dashboard_bp.route("/", methods=["GET"])
def dashboard():
    return render_template_string(HTML)


@dashboard_bp.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "online",
        "service": "AIDA Backend Dashboard",
        "memory": "active",
        "rag": "enabled",
        "analytics": "ready",
        "emotion_tracking": "enabled"
    })