import streamlit as st
import requests
import os
from dotenv import load_dotenv
"""
Progress tracking page - Student learning analytics.
"""

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Chat - AI Tutor", page_icon="💬", layout="wide")

st.title("💬 Chat with AI Tutor")

# Check if the student is logged in
if "student_id" not in st.session_state or st.session_state.student_id is None:
    st.warning("Please login from the home page first!")
    st.stop()

st.sidebar.header("🎯 Select Topic")
topic_options = {
    "Any Topic (Auto-detect)": None,
    "Operations Research": "operations_research",
    "Mathematical Modeling": "mathematical_modeling",
    "Linear Programming": "linear_programming",
    "Integer Programming": "integer_programming",
    "Nonlinear Programming": "nonlinear_programming"
}

selected_topic = st.sidebar.selectbox(
    "Focus on specific topic:",
    options=list(topic_options.keys())
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
            try:
                payload = {
                    "student_id": st.session_state.student_id,
                    "message": prompt,
                    "conversation_id": st.session_state.chat_conversation_id
                }

                if topic_options[selected_topic]:
                    payload["topic"] = topic_options[selected_topic]

                response = requests.post(f"{BACKEND_URL}/chat", json=payload)

                if response.status_code == 200:
                    data = response.json()
                    st.markdown(data["response"])
                    st.caption(f"Agent: {data['agent_type']}")

                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": data["response"],
                        "agent_type": data["agent_type"]
                    })
                    st.session_state.chat_conversation_id = data["conversation_id"]
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Failed to get response: {e}")

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
questions