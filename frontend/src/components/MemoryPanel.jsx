import React from "react";

export default function MemoryPanel({
    memories = []
}) {

    return (
        <div style={styles.panel}>

            <h3>🧠 Retrieved Memories</h3>

            {
                memories.length === 0 && (
                    <p>No memories retrieved.</p>
                )
            }

            {
                memories.map((memory, index) => (

                    <div
                        key={index}
                        style={styles.memory}
                    >
                        <div>
                            {memory.content}
                        </div>

                        <small>
                            Score:
                            {" "}
                            {memory.score}
                        </small>
                    </div>
                ))
            }
        </div>
    );
}

const styles = {

    panel: {
        background: "#111827",
        padding: "15px",
        borderRadius: "12px",
        color: "white",
        marginTop: "15px"
    },

    memory: {
        padding: "10px",
        marginTop: "10px",
        background: "#1f2937",
        borderRadius: "8px"
    }
};