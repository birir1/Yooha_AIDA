// ============================================================
// App.jsx
// AIDA FRONTEND — MODERN + EMOTIONALLY AWARE UI
// FULLY UPDATED VERSION
// ============================================================

import { useEffect, useRef, useState } from "react";
import apiService from "./services/apiService";

import ChatWindow from "./components/ChatWindow";
import EmotionIndicator from "./components/EmotionIndicator";
import MemoryPanel from "./components/MemoryPanel";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import SettingsPanel from "./components/SettingsPanel";
import VoiceWave from "./components/VoiceWave";

// ============================================================
// MAIN APP
// ============================================================

export default function App() {

    // ========================================================
    // STATE
    // ========================================================

    const [messages, setMessages] = useState([
        {
            role: "assistant",
            text: "Hey there 👋 I'm AIDA. How are you feeling today?"
        }
    ]);

    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    const [emotion, setEmotion] = useState("neutral");
    const [memories, setMemories] = useState([]);

    const [backendStatus, setBackendStatus] = useState("checking");

    const [sessionId] = useState(() => crypto.randomUUID());

    const textareaRef = useRef(null);

    // ========================================================
    // HEALTH CHECK
    // ========================================================

    useEffect(() => {

        const runHealthCheck = async () => {

            try {

                const health = await apiService.healthCheck();

                if (health?.status === "ok") {
                    setBackendStatus("online");
                } else {
                    setBackendStatus("offline");
                }

            } catch {
                setBackendStatus("offline");
            }
        };

        runHealthCheck();

        const interval = setInterval(runHealthCheck, 10000);

        return () => clearInterval(interval);

    }, []);

    // ========================================================
    // AUTO RESIZE TEXTAREA
    // ========================================================

    useEffect(() => {

        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height =
                textareaRef.current.scrollHeight + "px";
        }

    }, [input]);

    // ========================================================
    // SEND MESSAGE
    // ========================================================

    const sendMessage = async () => {

        if (!input.trim() || loading) return;

        const userMessage = input.trim();

        // ====================================================
        // ADD USER MESSAGE
        // ====================================================

        setMessages(prev => [
            ...prev,
            {
                role: "user",
                text: userMessage
            }
        ]);

        setInput("");
        setLoading(true);

        try {

            const data = await apiService.sendMessage(
                userMessage,
                "sospeter",
                sessionId,
                5
            );

            // ====================================================
            // HANDLE ERRORS
            // ====================================================

            if (data?.error) {

                setMessages(prev => [
                    ...prev,
                    {
                        role: "assistant",
                        text:
                            "I'm having trouble connecting to my backend right now."
                    }
                ]);

                setBackendStatus("offline");

                return;
            }

            // ====================================================
            // ASSISTANT RESPONSE
            // ====================================================

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    text:
                        data?.response ||
                        "I'm here with you."
                }
            ]);

            // ====================================================
            // EMOTION
            // ====================================================

            if (data?.emotion) {

                const detectedEmotion =
                    typeof data.emotion === "string"
                        ? data.emotion
                        : data.emotion?.emotion;

                if (detectedEmotion) {
                    setEmotion(detectedEmotion);
                }
            }

            // ====================================================
            // MEMORIES
            // ====================================================

            if (Array.isArray(data?.memories)) {
                setMemories(data.memories);
            }

            setBackendStatus("online");

        } catch (error) {

            console.error(error);

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    text:
                        "Something went wrong while trying to respond."
                }
            ]);

            setBackendStatus("offline");

        } finally {
            setLoading(false);
        }
    };

    // ========================================================
    // ENTER KEY
    // ========================================================

    const handleKeyDown = (e) => {

        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    // ========================================================
    // STATUS COLORS
    // ========================================================

    const getStatusColor = () => {

        if (backendStatus === "online") {
            return "#22c55e";
        }

        if (backendStatus === "offline") {
            return "#ef4444";
        }

        return "#f59e0b";
    };

    // ========================================================
    // UI
    // ========================================================

    return (
        <div style={styles.page}>

            {/* ================================================= */}
            {/* SIDEBAR */}
            {/* ================================================= */}

            <div style={styles.sidebar}>

                <div style={styles.logoSection}>

                    <div style={styles.logo}>
                        🧠
                    </div>

                    <div>
                        <h1 style={styles.logoTitle}>
                            AIDA
                        </h1>

                        <p style={styles.logoSub}>
                            Emotionally aware memory assistant
                        </p>
                    </div>

                </div>

                {/* STATUS */}

                <div style={styles.statusCard}>

                    <div style={styles.statusRow}>
                        <span>Backend</span>

                        <div style={styles.statusIndicator}>
                            <div
                                style={{
                                    ...styles.statusDot,
                                    background: getStatusColor()
                                }}
                            />

                            <span>
                                {backendStatus === "online"
                                    ? "Online"
                                    : backendStatus === "offline"
                                        ? "Offline"
                                        : "Checking"}
                            </span>
                        </div>
                    </div>

                    <div style={styles.statusRow}>
                        <span>Emotion</span>
                        <span style={styles.statusValue}>
                            {emotion}
                        </span>
                    </div>

                    <div style={styles.statusRow}>
                        <span>Memories</span>
                        <span style={styles.statusValue}>
                            {memories.length}
                        </span>
                    </div>

                </div>

                {/* PANELS */}

                <div style={styles.sidePanels}>
                    <EmotionIndicator emotion={emotion} />
                    <MemoryPanel memories={memories} />
                    <SettingsPanel />
                </div>

            </div>

            {/* ================================================= */}
            {/* MAIN */}
            {/* ================================================= */}

            <div style={styles.main}>

                {/* TOP BAR */}

                <div style={styles.topBar}>

                    <div>

                        <h2 style={styles.mainTitle}>
                            🧠 Memory AI Assistant
                        </h2>

                        <p style={styles.mainSubtitle}>
                            AIDA is here to support, remember, and assist you.
                        </p>

                    </div>

                    <VoiceWave active={loading} />

                </div>

                {/* DASHBOARD */}

                <AnalyticsDashboard />

                {/* CHAT */}

                <div style={styles.chatWrapper}>
                    <ChatWindow messages={messages} />
                </div>

                {/* INPUT */}

                <div style={styles.inputWrapper}>

                    <textarea
                        ref={textareaRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Talk to AIDA..."
                        style={styles.input}
                        rows={1}
                        disabled={loading}
                    />

                    <button
                        onClick={sendMessage}
                        disabled={loading}
                        style={{
                            ...styles.sendButton,
                            opacity: loading ? 0.7 : 1
                        }}
                    >
                        {loading ? "..." : "Send"}
                    </button>

                </div>

            </div>

        </div>
    );
}

// ============================================================
// STYLES
// ============================================================

const styles = {

    page: {
        display: "flex",
        minHeight: "100vh",
        background: "#020617",
        color: "white",
        fontFamily: "Inter, Arial, sans-serif"
    },

    // ========================================================
    // SIDEBAR
    // ========================================================

    sidebar: {
        width: "320px",
        background: "#0f172a",
        borderRight: "1px solid #1e293b",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "20px"
    },

    logoSection: {
        display: "flex",
        alignItems: "center",
        gap: "16px"
    },

    logo: {
        width: "58px",
        height: "58px",
        borderRadius: "18px",
        background: "linear-gradient(135deg, #2563eb, #7c3aed)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "28px"
    },

    logoTitle: {
        margin: 0,
        fontSize: "26px",
        fontWeight: "700"
    },

    logoSub: {
        margin: "4px 0 0 0",
        color: "#94a3b8",
        fontSize: "14px"
    },

    statusCard: {
        background: "#111827",
        borderRadius: "18px",
        padding: "18px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        border: "1px solid #1f2937"
    },

    statusRow: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        fontSize: "15px"
    },

    statusIndicator: {
        display: "flex",
        alignItems: "center",
        gap: "8px"
    },

    statusDot: {
        width: "10px",
        height: "10px",
        borderRadius: "999px"
    },

    statusValue: {
        color: "#cbd5e1"
    },

    sidePanels: {
        display: "flex",
        flexDirection: "column",
        gap: "18px",
        overflowY: "auto"
    },

    // ========================================================
    // MAIN
    // ========================================================

    main: {
        flex: 1,
        display: "flex",
        flexDirection: "column",
        padding: "24px",
        overflow: "hidden"
    },

    topBar: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "20px"
    },

    mainTitle: {
        margin: 0,
        fontSize: "28px",
        fontWeight: "700"
    },

    mainSubtitle: {
        marginTop: "6px",
        color: "#94a3b8"
    },

    chatWrapper: {
        flex: 1,
        overflow: "hidden",
        marginTop: "20px",
        marginBottom: "20px",
        borderRadius: "20px",
        background: "#0f172a",
        border: "1px solid #1e293b",
        padding: "10px"
    },

    // ========================================================
    // INPUT
    // ========================================================

    inputWrapper: {
        display: "flex",
        alignItems: "flex-end",
        gap: "14px",
        background: "#0f172a",
        padding: "14px",
        borderRadius: "20px",
        border: "1px solid #1e293b"
    },

    input: {
        flex: 1,
        border: "none",
        outline: "none",
        resize: "none",
        background: "transparent",
        color: "white",
        fontSize: "16px",
        lineHeight: "1.5",
        maxHeight: "180px",
        overflowY: "auto",
        fontFamily: "inherit"
    },

    sendButton: {
        background: "linear-gradient(135deg, #2563eb, #7c3aed)",
        border: "none",
        color: "white",
        padding: "14px 22px",
        borderRadius: "14px",
        cursor: "pointer",
        fontWeight: "700",
        fontSize: "15px",
        minWidth: "90px"
    }
};