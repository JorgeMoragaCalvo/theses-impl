import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import get_api_client
from utils.constants import TOPIC_OPTIONS, TOPICS_LIST
"""
Chat page - Detailed conversation interface with topic selection.
"""

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Get API client
api_client = get_api_client(BACKEND_URL)

st.set_page_config(page_title="Chat - AI Tutor", page_icon="💬", layout="wide")

st.title("💬 Chat with AI Tutor")

# Check if the user is authenticated
if not api_client.is_authenticated():
    st.warning("Please login from the home page first!")
    st.info("Click the link in the sidebar to go to the home page.")
    st.stop()

st.sidebar.header("🎯 Select Topic")
# TODO: Implement auto-detect topic feature in the future

selected_topic = st.sidebar.selectbox(
    "Focus on specific topic:",
    options=TOPICS_LIST
)

# Initialize chat
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
    st.session_state.chat_conversation_id = None

# Display chat
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "agent_type" in message and message["role"] == "assistant":
            st.caption(f"Agent: {message['agent_type']}")

# Chat input
if prompt := st.chat_input("Ask your question..."):
    # Add the user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("AI Tutor is thinking..."):
            # Use the authenticated API client (student_id extracted from token)
            success, data = api_client.post("/chat", json_data={
                "message": prompt,
                "conversation_id": st.session_state.chat_conversation_id,
                "topic": TOPIC_OPTIONS[selected_topic]
            })

            if success:
                st.markdown(data["response"])
                st.caption(f"Agent: {data['agent_type']}")

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": data["response"],
                    "agent_type": data["agent_type"]
                })
                st.session_state.chat_conversation_id = data["conversation_id"]
            else:
                error_msg = data.get("detail", data.get("error", "Failed to get response"))
                st.error(f"Error: {error_msg}")

# Sidebar controls
with st.sidebar:
    st.divider()

    if st.button("🗑️ Clear Conversation"):
        st.session_state.chat_messages = []
        st.session_state.chat_conversation_id = None
        st.rerun()

    st.divider()

    st.subheader("💡 Tips")
    st.markdown("""
    - Be specific in your questions
    - Ask for examples or step-by-step solutions
    - Request different explanation styles if needed
    - You can ask follow-up questions
    """)