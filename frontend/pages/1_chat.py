import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import get_api_client
from utils.constants import TOPIC_OPTIONS, TOPICS_LIST
"""
Página de chat - Interfaz de conversación detallada con selección de temas.
"""

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Get API client
api_client = get_api_client(BACKEND_URL)

st.set_page_config(page_title="Chat - AI Tutor", page_icon="💬", layout="wide")

st.title("💬 Chatea con el tutor de IA")

# Check if the user is authenticated
if not api_client.is_authenticated():
    st.warning("¡Primero inicia sesión desde la página de inicio!")
    st.info("Haga clic en el enlace de la barra lateral para ir a la página de inicio.")
    st.stop()

st.sidebar.header("🎯 Select Topic")
# TODO: Implement auto-detect topic feature in the future

selected_topic = st.sidebar.selectbox(
    "Elige un tema específico:",
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
if prompt := st.chat_input("Haz tu pregunta..."):
    # Add the user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("El Tutor de IA está pensando..."):
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

    if st.button("🗑️ Limpiar conversación"):
        st.session_state.chat_messages = []
        st.session_state.chat_conversation_id = None
        st.rerun()

    st.divider()

    st.subheader("💡 Tips")
    st.markdown("""
    - Se específico en tus preguntas
    - Pide ejemplos o soluciones paso a paso
    - Solicita diferentes estilos de explicación si es necesario
    - Puedes hacer preguntas de seguimiento
    """)
