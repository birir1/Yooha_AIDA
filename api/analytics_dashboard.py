# ============================================================
# analytics_dashboard.py
# Backend Visual Analytics Dashboard (HTML)
# ============================================================

from flask import Blueprint, Response
import json

from memory.memory_manager import MemoryManager

analytics_ui_bp = Blueprint("analytics_ui", __name__)
memory_manager = MemoryManager()


# ============================================================
# DASHBOARD ROUTE (VISUAL UI)
# ============================================================

@analytics_ui_bp.route("/dashboard", methods=["GET"])
def dashboard():

    try:

        stats = memory_manager.db.get_stats()
        memories = memory_manager.db.get_all_memories()

        # -------------------------------
        # MEMORY COUNT BY DAY
        # -------------------------------
        growth = {}

        for m in memories:
            ts = m.get("timestamp", "")
            if ts:
                day = ts[:10]
                growth[day] = growth.get(day, 0) + 1

        labels = list(growth.keys())
        values = list(growth.values())

        # -------------------------------
        # SIMPLE HTML + CHART.JS
        # -------------------------------
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AIDA Analytics Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    font-family: Arial;
                    background: #0f172a;
                    color: white;
                    padding: 20px;
                }}
                .card {{
                    background: #111827;
                    padding: 20px;
                    border-radius: 12px;
                    margin-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    border-bottom: 1px solid #333;
                    padding: 10px;
                    text-align: left;
                }}
            </style>
        </head>

        <body>

            <h1>📊 AIDA Backend Analytics Dashboard</h1>

            <div class="card">
                <h2>📦 Database Stats</h2>
                <pre>{json.dumps(stats, indent=2)}</pre>
            </div>

            <div class="card">
                <h2>📈 Memory Growth Over Time</h2>
                <canvas id="chart"></canvas>
            </div>

            <div class="card">
                <h2>📋 Recent Memories</h2>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Content</th>
                        <th>Importance</th>
                    </tr>

                    {"".join([
                        f"<tr><td>{m.get('id','-')}</td><td>{m.get('content','')[:80]}</td><td>{m.get('importance',0)}</td></tr>"
                        for m in memories[-10:]
                    ])}
                </table>
            </div>

            <script>
                const ctx = document.getElementById('chart');

                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(labels)},
                        datasets: [{{
                            label: 'Memory Growth',
                            data: {json.dumps(values)},
                            borderColor: '#60a5fa',
                            fill: false
                        }}]
                    }}
                }});
            </script>

        </body>
        </html>
        """

        return Response(html, mimetype="text/html")

    except Exception as e:

        return f"<h1>Error loading dashboard</h1><pre>{str(e)}</pre>", 500