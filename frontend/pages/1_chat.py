import base64
import csv
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))  # noqa: E402

from utils.activity_tracker import (
    PAGE_CHAT,
    flush_events,
    track_chat_message,
    track_interaction,
    track_page_visit,
)
from utils.api_client import get_api_client
from utils.constants import TOPIC_OPTIONS, TOPICS_LIST
from utils.idle_detector import inject_idle_detector
from utils.pages_registry import get_home_page

"""
Página de chat - Interfaz de conversación detallada con selección de temas.
"""

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Get API client
api_client = get_api_client(BACKEND_URL)

# Registro temporal de latencias para el experimento RNF7 (activar con RNF7_LOG=true)
RNF7_LOG = os.getenv("RNF7_LOG", "").lower() == "true"
RNF7_LOG_FILE = Path(
    os.getenv("RNF7_LOG_FILE", str(Path(__file__).parent.parent / "rnf7_latencias.csv"))
)


def log_rnf7_latency(
    tema: str, timestamp_inicio: str, timestamp_fin: str, latencia_ms: float
) -> None:
    """Append one latency measurement to the RNF7 CSV file."""
    nuevo = not RNF7_LOG_FILE.exists()
    id_pregunta = (
        1
        if nuevo
        else sum(1 for _ in RNF7_LOG_FILE.open(encoding="utf-8"))
    )
    with RNF7_LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if nuevo:
            writer.writerow(
                ["id_pregunta", "tema", "timestamp_inicio", "timestamp_fin", "latencia_ms"]
            )
        writer.writerow(
            [id_pregunta, tema, timestamp_inicio, timestamp_fin, round(latencia_ms, 1)]
        )


_BASE64_IMAGE_RE = re.compile(
    r"!\[([^\]]*)\]\(data:image/png;base64,([A-Za-z0-9+/=]+)\)"
)
_BASE64_LEFTOVER_RE = re.compile(
    r"!\[[^\]]*\]\(data:image/png;base64,[\s\S]*?\)"
)


def render_message(content: str) -> None:
    """Render a chat message, extracting any embedded base64 PNG images."""
    last = 0
    for match in _BASE64_IMAGE_RE.finditer(content):
        text_before = content[last : match.start()]
        if text_before.strip():
            st.markdown(_BASE64_LEFTOVER_RE.sub("", text_before))
        caption, b64 = match.group(1), match.group(2)
        st.image(base64.b64decode(b64), caption=caption or None)
        last = match.end()
    remaining = _BASE64_LEFTOVER_RE.sub("", content[last:])
    if remaining.strip():
        st.markdown(remaining)


st.html("""
    <script>
    function alignUserMessages() {
        const messages = window.parent.document.querySelectorAll('[data-testid="stChatMessage"]');
        messages.forEach(msg => {
            const avatarEl = msg.firstElementChild;
            if (avatarEl && avatarEl.textContent.includes('🧑‍🎓')) {
                msg.style.setProperty('flex-direction', 'row-reverse', 'important');
            }
        });
    }
    const chatObserver = new MutationObserver(alignUserMessages);
    chatObserver.observe(window.parent.document.body, { childList: true, subtree: true });
    alignUserMessages();
    </script>
""")

st.title("💬 Chatea con el tutor de IA")

# Check if the user is authenticated
if not api_client.is_authenticated():
    st.warning("¡Primero inicia sesión desde la página de inicio!")
    st.info("Haga clic en el enlace de la barra lateral para ir a la página de inicio.")
    st.stop()

# Analytics tracking
track_page_visit(PAGE_CHAT)
inject_idle_detector(backend_url=BACKEND_URL)

st.sidebar.header("🎯 Select Topic")
# TODO: Implement auto-detect topic feature in the future

selected_topic = st.sidebar.selectbox("Elige un tema específico:", options=TOPICS_LIST)

# Initialize chat
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
    st.session_state.chat_conversation_id = None

# Display chat
for message in st.session_state.chat_messages:
    with st.chat_message(
        message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🎓"
    ):
        render_message(message["content"])
        if "agent_type" in message and message["role"] == "assistant":
            st.caption(f"Agent: {message['agent_type']}")

# Chat input
if prompt := st.chat_input(placeholder="Haz tu pregunta..."):
    # Add the user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant", avatar="🎓"):
        with st.spinner("El Tutor de IA está pensando..."):
            # Use the authenticated API client (student_id extracted from token)
            timestamp_inicio = datetime.now(timezone.utc).isoformat()
            t0 = time.perf_counter()
            success, data = api_client.post(
                "/chat",
                json_data={
                    "message": prompt,
                    "conversation_id": st.session_state.chat_conversation_id,
                    "topic": TOPIC_OPTIONS[selected_topic],
                },
            )
            latencia_ms = (time.perf_counter() - t0) * 1000
            timestamp_fin = datetime.now(timezone.utc).isoformat()

            if success:
                if RNF7_LOG:
                    log_rnf7_latency(
                        TOPIC_OPTIONS[selected_topic],
                        timestamp_inicio,
                        timestamp_fin,
                        latencia_ms,
                    )
                render_message(data["response"])
                st.caption(f"Agent: {data['agent_type']}")

                st.session_state.chat_messages.append(
                    {
                        "role": "assistant",
                        "content": data["response"],
                        "agent_type": data["agent_type"],
                    }
                )
                st.session_state.chat_conversation_id = data["conversation_id"]
                track_chat_message(
                    PAGE_CHAT, TOPIC_OPTIONS[selected_topic], data["conversation_id"]
                )
            else:
                error_msg = data.get(
                    "detail", data.get("error", "Failed to get response")
                )
                st.error(f"Error: {error_msg}")

# Sidebar controls
with st.sidebar:
    st.divider()

    if st.button("🗑️ Limpiar conversación"):
        track_interaction("clear_conversation", PAGE_CHAT)
        flush_events()
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

    st.divider()
    st.html("""
        <script>
        function styleLogoutBtn() {
            const buttons = window.parent.document.querySelectorAll(
                'button[data-testid="stBaseButton-secondary"]'
            );
            buttons.forEach(btn => {
                if (btn.textContent.trim() === 'Logout') {
                    btn.style.setProperty('background-color', '#ff4b4b', 'important');
                    btn.style.setProperty('color', 'white', 'important');
                    btn.style.setProperty('border-color', '#ff4b4b', 'important');
                }
            });
        }
        // Retry until the button exists in the DOM
        const interval = setInterval(() => {
            const btn = window.parent.document.querySelector(
                'button[data-testid="stBaseButton-secondary"]'
            );
            if (btn) { styleLogoutBtn(); clearInterval(interval); }
        }, 100);
        setTimeout(() => clearInterval(interval), 5000);
        </script>
    """)
    if st.button("Logout", key="logout_btn", type="primary"):
        flush_events()
        api_client.logout()
        home = get_home_page()
        if home is not None:
            st.switch_page(home)
        else:
            st.rerun()
