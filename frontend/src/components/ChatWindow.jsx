import React, { useState } from "react";
import apiService from "../services/apiService";

export default function ChatWindow() {

    const [messages, setMessages] = useState([
        {
            sender: "assistant",
            text: "👋 Hello! I am your Memory-Augmented AI Assistant."
        }
    ]);

    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    const [sessionId] = useState(() => {
        try {
            return crypto?.randomUUID
                ? crypto.randomUUID()
                : `session_${Date.now()}`;
        } catch {
            return `session_${Date.now()}`;
        }
    });

    const handleSend = async () => {

        if (!input || !input.trim() || loading) return;

        const userText = input.trim();

        // add user message immediately
        setMessages(prev => [
            ...prev,
            { sender: "user", text: userText }
        ]);

        setInput("");
        setLoading(true);

        try {
            console.log("📤 Sending message:", userText);

            const res = await apiService.sendMessage(
                userText,
                "sospeter",
                sessionId,
                5
            );

            console.log("📥 Raw API response:", res);

            // normalize backend response safely
            const data = res?.data || res || {};

            const botText =
                data.response ||
                data.message ||
                data.context ||
                data.error ||
                JSON.stringify(data) ||
                "⚠️ Empty response from backend";

            setMessages(prev => [
                ...prev,
                { sender: "assistant", text: botText }
            ]);

        } catch (error) {

            console.error("❌ Chat request failed:", error);

            const errorText =
                error?.response?.data?.message ||
                error?.message ||
                "❌ Backend connection failed";

            setMessages(prev => [
                ...prev,
                { sender: "assistant", text: errorText }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>

            <h1 style={styles.title}>
                🧠 Memory AI Assistant
            </h1>

            <div style={styles.chatBox}>

                {messages.map((msg, i) => (
                    <div
                        key={i}
                        style={{
                            textAlign: msg.sender === "user" ? "right" : "left",
                            marginBottom: 12
                        }}
                    >
                        <div style={{
                            display: "inline-block",
                            padding: 12,
                            borderRadius: 10,
                            background: msg.sender === "user"
                                ? "#2563eb"
                                : "#1f2937",
                            maxWidth: "80%",
                            whiteSpace: "pre-wrap"
                        }}>
                            {msg.text}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div style={{ opacity: 0.7 }}>
                        Thinking...
                    </div>
                )}

            </div>

            <div style={styles.inputRow}>

                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            e.preventDefault();
                            handleSend();
                        }
                    }}
                    placeholder="Type something..."
                    style={styles.input}
                />

                <button
                    onClick={handleSend}
                    disabled={loading}
                    style={styles.button}
                >
                    {loading ? "..." : "Send"}
                </button>

            </div>
        </div>
    );
}

// ============================
// STYLES
// ============================

const styles = {
    container: {
        width: "100%",
        maxWidth: 900,
        margin: "0 auto",
        padding: 20,
        color: "white"
    },
    title: {
        marginBottom: 20
    },
    chatBox: {
        height: "70vh",
        overflowY: "auto",
        background: "#0f172a",
        border: "1px solid #334155",
        borderRadius: 12,
        padding: 20,
        marginBottom: 20
    },
    inputRow: {
        display: "flex",
        gap: 10
    },
    input: {
        flex: 1,
        padding: 14,
        borderRadius: 10,
        border: "none",
        outline: "none",
        fontSize: 16
    },
    button: {
        padding: "14px 20px",
        borderRadius: 10,
        border: "none",
        background: "#10b981",
        color: "white",
        fontWeight: "bold",
        cursor: "pointer"
    }
};