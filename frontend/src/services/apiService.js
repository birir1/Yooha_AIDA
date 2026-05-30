// ============================================================
// apiService.js
// PRODUCTION FRONTEND API SERVICE
// ============================================================

const API_BASE = "/api";

// ============================================================
// SAFE JSON PARSER
// ============================================================

function safeParse(raw) {

    try {
        return JSON.parse(raw);
    } catch {

        return {
            status: "error",
            response: raw || "",
            raw
        };
    }
}

// ============================================================
// GENERATE SESSION ID
// ============================================================

function generateSessionId() {

    return `session_${Date.now()}_${Math.random()
        .toString(36)
        .substring(2, 8)}`;
}

// ============================================================
// GENERATE USER ID
// ============================================================

function generateUserId() {

    return `user_${Math.random()
        .toString(36)
        .substring(2, 10)}`;
}

// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage(
    message,
    user_id,
    session_id,
    top_k = 5
) {

    try {

        // ====================================================
        // VALIDATION
        // ====================================================

        if (!message || !message.trim()) {

            return {
                success: false,
                error: "Message cannot be empty"
            };
        }

        // ====================================================
        // AUTO IDS
        // ====================================================

        if (!user_id) {
            user_id = generateUserId();
        }

        if (!session_id) {
            session_id = generateSessionId();
        }

        // ====================================================
        // DEBUG
        // ====================================================

        console.log("🚀 Sending Message");

        console.log({
            endpoint: `${API_BASE}/chat/`,
            message,
            user_id,
            session_id,
            top_k
        });

        // ====================================================
        // REQUEST
        // ====================================================

        const response = await fetch(`${API_BASE}/chat/`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message,
                user_id,
                session_id,
                top_k
            })
        });

        // ====================================================
        // RAW RESPONSE
        // ====================================================

        const raw = await response.text();

        console.log("📦 RAW RESPONSE:", raw);

        const data = safeParse(raw);

        console.log("✅ PARSED RESPONSE:", data);

        // ====================================================
        // ERROR RESPONSE
        // ====================================================

        if (!response.ok) {

            return {
                success: false,

                status: response.status,

                error:
                    data?.message ||
                    data?.error ||
                    "Backend request failed",

                data
            };
        }

        // ====================================================
        // SUCCESS RESPONSE
        // ====================================================

        return {

            success: true,

            status: response.status,

            response:
                data?.response ||
                data?.data?.response ||
                "No response generated",

            emotion:
                data?.emotion ||
                data?.data?.emotion ||
                "neutral",

            memories:
                data?.memories ||
                data?.data?.memories ||
                [],

            memory_count:
                data?.memory_count ||
                data?.data?.memory_count ||
                0,

            context:
                data?.context ||
                data?.data?.context ||
                "",

            user_id,

            session_id,

            raw: data
        };

    } catch (error) {

        console.error("❌ NETWORK ERROR:", error);

        return {

            success: false,

            error:
                error?.message ||
                "Server not reachable",

            offline: true
        };
    }
}

// ============================================================
// HEALTH CHECK
// ============================================================

async function healthCheck() {

    try {

        console.log("🩺 Checking backend health...");

        const response = await fetch(`${API_BASE}/health`, {
            method: "GET"
        });

        const raw = await response.text();

        const data = safeParse(raw);

        if (!response.ok) {

            return {
                online: false,
                status: "offline",
                error:
                    data?.message ||
                    "Health check failed"
            };
        }

        return {

            online: true,

            status:
                data?.status ||
                "ok",

            services:
                data?.services || {},

            version:
                data?.version || "unknown",

            data
        };

    } catch (error) {

        console.error("❌ HEALTH CHECK FAILED:", error);

        return {

            online: false,

            status: "offline",

            error:
                error?.message ||
                "Backend unreachable"
        };
    }
}

// ============================================================
// GET MEMORY STATS
// ============================================================

async function getMemoryStats() {

    try {

        const response = await fetch(
            `${API_BASE}/debug/memory/stats`
        );

        const raw = await response.text();

        const data = safeParse(raw);

        return data;

    } catch (error) {

        console.error("❌ MEMORY STATS ERROR:", error);

        return {
            status: "error",
            error: error.message
        };
    }
}

// ============================================================
// FETCH SESSION MEMORIES
// ============================================================

async function getSessionMemories(session_id) {

    try {

        if (!session_id) {
            return [];
        }

        const response = await fetch(
            `${API_BASE}/memory/${session_id}`
        );

        const raw = await response.text();

        const data = safeParse(raw);

        return (
            data?.memories ||
            data?.data?.memories ||
            []
        );

    } catch (error) {

        console.error(
            "❌ SESSION MEMORY FETCH ERROR:",
            error
        );

        return [];
    }
}

// ============================================================
// CLEAR SESSION
// ============================================================

async function clearSession(session_id) {

    try {

        const response = await fetch(
            `${API_BASE}/memory/clear/${session_id}`,
            {
                method: "DELETE"
            }
        );

        const raw = await response.text();

        return safeParse(raw);

    } catch (error) {

        console.error(
            "❌ CLEAR SESSION ERROR:",
            error
        );

        return {
            status: "error",
            error: error.message
        };
    }
}

// ============================================================
// EXPORTS
// ============================================================

export default {

    sendMessage,

    healthCheck,

    getMemoryStats,

    getSessionMemories,

    clearSession,

    generateSessionId,

    generateUserId
};