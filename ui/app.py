import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api/chat"

st.set_page_config(page_title="Memory AI Assistant", layout="wide")

st.title("🧠 Memory-Augmented AI Assistant")

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# INPUT
# -----------------------------
user_input = st.text_input("Type something...")

if st.button("Send") and user_input:

    payload = {
        "message": user_input,
        "session_id": st.session_state.session_id,
        "user_id": "demo_user"
    }

    try:
        res = requests.post(API_URL, json=payload, timeout=10)

        # IMPORTANT: handle backend errors safely
        data = res.json()

        if res.status_code != 200:
            st.error(data.get("message", "Backend error"))
        else:
            st.session_state.session_id = data.get("session_id")

            st.session_state.messages.append(("user", user_input))
            st.session_state.messages.append(("assistant", data.get("response")))

    except Exception as e:
        st.error(f"❌ Cannot reach backend server: {str(e)}")

# -----------------------------
# CHAT HISTORY
# -----------------------------
for role, msg in st.session_state.messages:
    if role == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**AI:** {msg}")