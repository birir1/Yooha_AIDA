import React, { useEffect, useState } from "react";

export default function AnalyticsDashboard() {

    const ANALYTICS_URL = "/api/analytics/";
    const BASE_URL = "http://127.0.0.1:8001";

    // ✅ ADDED: live data state
    const [overview, setOverview] = useState(null);
    const [health, setHealth] = useState(null);

    // ✅ ADDED: fetch analytics
    useEffect(() => {

        fetch(`${BASE_URL}/api/analytics/overview`)
            .then(res => res.json())
            .then(data => setOverview(data.overview || {}))
            .catch(() => {});

        fetch(`${BASE_URL}/api/health`)
            .then(res => res.json())
            .then(data => setHealth(data))
            .catch(() => {});

    }, []);

    return (
        <div style={styles.card}>

            <h3>📊 Analytics Dashboard</h3>

            <div style={styles.grid}>

                <div style={styles.metric}>
                    <h2>LLM</h2>
                    <p>{health?.services?.llm_service || "Connected"}</p>
                </div>

                <div style={styles.metric}>
                    <h2>Memory</h2>
                    <p>{health?.services?.memory_manager || "Active"}</p>
                </div>

                <div style={styles.metric}>
                    <h2>RAG</h2>
                    <p>{health?.services?.rag_pipeline || "Enabled"}</p>
                </div>

            </div>

            {/* ADDED: Live stats (minimal extension) */}
            <div style={{ marginTop: "15px", color: "#9ca3af" }}>
                <p>📦 Indexed Memories: {overview?.retriever_indexed_memories ?? "..."}</p>
                <p>👥 Active Sessions: {overview?.active_sessions ?? "..."}</p>
            </div>

            {/* ADDED: Analytics API link */}
            <div style={{ marginTop: "15px", textAlign: "center" }}>
                <a
                    href={ANALYTICS_URL}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                        color: "#60a5fa",
                        textDecoration: "none",
                        fontWeight: "bold"
                    }}
                >
                    Open Full Analytics API →
                </a>
            </div>

        </div>
    );
}

const styles = {

    card: {
        background: "#111827",
        color: "white",
        padding: "20px",
        borderRadius: "12px",
        marginBottom: "20px"
    },

    grid: {
        display: "flex",
        gap: "15px"
    },

    metric: {
        flex: 1,
        background: "#1f2937",
        padding: "15px",
        borderRadius: "10px",
        textAlign: "center"
    }
};