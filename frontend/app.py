import streamlit as st
import requests

API_URL = "http://localhost:8000/api/chat"

st.set_page_config(page_title="Memory AI Assistant", layout="wide")

st.title("🧠 Memory-Augmented AI Assistant")

# Session state
if "chat" not in st.session_state:
    st.session_state.chat = []

if "user_id" not in st.session_state:
    st.session_state.user_id = "default_user"


# Sidebar
st.sidebar.header("Settings")
st.session_state.user_id = st.sidebar.text_input("User ID", "default_user")


# Chat input
user_input = st.text_input("Say something:")

if st.button("Send") and user_input:

    payload = {
        "message": user_input,
        "user_id": st.session_state.user_id
    }

    try:
        res = requests.post(API_URL, json=payload, timeout=30)
        data = res.json()

        assistant_reply = data.get("response", "No response")

    except Exception as e:
        assistant_reply = f"Error: {str(e)}"

    st.session_state.chat.append(("You", user_input))
    st.session_state.chat.append(("AI", assistant_reply))


# Chat history display
for role, msg in st.session_state.chat:
    if role == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 AI:** {msg}")