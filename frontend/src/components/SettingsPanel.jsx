import React from "react";

export default function SettingsPanel() {

    return (
        <div style={styles.panel}>

            <h3>⚙ Settings</h3>

            <div style={{ marginTop: "10px" }}>
                Memory-Augmented AI Assistant
            </div>

        </div>
    );
}

const styles = {

    panel: {
        background: "#111827",
        color: "white",
        padding: "15px",
        borderRadius: "12px",
        marginTop: "15px"
    }
};