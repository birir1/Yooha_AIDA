import React from "react";

export default function EmotionIndicator({
    emotion = "neutral"
}) {

    const getColor = () => {

        switch (emotion) {

            case "happy":
                return "#22c55e";

            case "sad":
                return "#3b82f6";

            case "angry":
                return "#ef4444";

            default:
                return "#94a3b8";
        }
    };

    return (
        <div
            style={{
                padding: "10px",
                borderRadius: "10px",
                background: "#1e293b",
                color: "white",
                marginBottom: "10px"
            }}
        >
            <strong>Emotion:</strong>

            <span
                style={{
                    marginLeft: "10px",
                    color: getColor()
                }}
            >
                {emotion}
            </span>
        </div>
    );
}