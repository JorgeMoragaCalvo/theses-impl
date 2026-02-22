import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent)) # noqa: E402

from utils.activity_tracker import PAGE_PROGRESS, track_page_visit
from utils.api_client import get_api_client
from utils.idle_detector import inject_idle_detector

"""
Página de seguimiento del progreso - análisis del aprendizaje de los estudiantes
"""
# Progress tracking page - Student learning analytics

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Get API client
api_client = get_api_client(BACKEND_URL)

st.set_page_config(page_title="Progress - AI Tutor", page_icon="📊", layout="wide")

st.title("📊 Tu progreso de aprendizaje")

# Check if the user is authenticated
if not api_client.is_authenticated():
    st.warning("Please login from the home page first!")
    st.info("Click the link in the sidebar to go to the home page.")
    st.stop()

# Analytics tracking
track_page_visit(PAGE_PROGRESS)
inject_idle_detector(backend_url=BACKEND_URL)

# Get student_id from the session
student_id = st.session_state.get("student_id")

# ============================================================================
# API HELPER FUNCTIONS
# ============================================================================

def fetch_student_progress(student_id: int):
    """Fetch comprehensive student progress metrics."""
    success, data = api_client.get(f"students/{student_id}/progress")
    if not success:
        st.error(f"Error fetching progress: {data.get('error', 'Unknown error')}")
        return None
    return data

# ============================================================================
# MAIN PAGE
# ============================================================================

# Fetch student data using the authenticated API
success, student_data = api_client.get(f"students/{student_id}")
if success:

        # Display student info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Name", student_data["name"])
        with col2:
            st.metric("Email", student_data["email"])
        with col3:
            created_date = datetime.fromisoformat(student_data["created_at"].replace("Z", "+00:00"))
            st.metric("Member Since", created_date.strftime("%Y-%m-%d"))

        st.divider()

        # Knowledge levels
        st.subheader("🎯 Niveles de conocimiento por tema")

        knowledge_levels = student_data.get("knowledge_levels", {})
        topic_names = {
            "operations_research": "Operations Research",
            "mathematical_modeling": "Mathematical Modeling",
            "linear_programming": "Linear Programming",
            "integer_programming": "Integer Programming",
            "nonlinear_programming": "Nonlinear Programming"
        }

        level_colors = {
            "beginner": "🔴",
            "intermediate": "🟡",
            "advanced": "🟢"
        }

        cols = st.columns(len(topic_names))

        for idx, (topic_key, topic_name) in enumerate(topic_names.items()):
            level = knowledge_levels.get(topic_key, "beginner")
            with cols[idx]:
                st.markdown(f"**{topic_name}**")
                st.markdown(f"{level_colors.get(level, '⚪')} {level.title()}")

        st.divider()

        # Fetch conversations using the authenticated API
        conv_success, conversations = api_client.get(f"students/{student_id}/conversations")

        st.subheader("💬Historial de conversaciones")
        if conv_success and conversations:
            st.metric("Conversaciones totales", len(conversations))

            # Show recent conversations
            st.markdown("#### Conversaciones recientes")

            for conv in conversations[:5]:
                with st.expander(
                    f"Conversation {conv['id']} - {conv.get('topic', 'General').replace('_', ' ').title()}"
                    f" - {datetime.fromisoformat(conv['started_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}"
                ):
                    st.write(f"**Status:** {'Active' if conv['is_active'] else 'Ended'}")
                    st.write(f"**Started:** {conv['started_at']}")
                    if conv.get('ended_at'):
                        st.write(f"**Ended:** {conv['ended_at']}")

                    # Load full conversation
                    if st.button("View Details", key=f"view_{conv['id']}"):
                        detail_success, detail_data = api_client.get(f"conversations/{conv['id']}")
                        if detail_success:
                            st.write(f"**Messages:** {len(detail_data.get('messages', []))}")
        elif conv_success:
            st.info("No conversations yet.")
        else:
            st.error(f"Failed to load conversations: {conversations.get('error', 'Unknown error')}")

        st.divider()

        # Learning Statistics
        st.subheader("📈 Estadísticas de aprendizaje")

        # Fetch progress data
        progress_data = fetch_student_progress(student_id)

        if progress_data is not None:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Mensajes",
                    progress_data.get("total_messages", 0)
                )

            with col2:
                st.metric(
                    "Problemas de práctica",
                    progress_data.get("total_assessments", 0)
                )

            with col3:
                avg_score = progress_data.get("average_score")
                if avg_score is not None:
                    st.metric(
                        "Puntuación media",
                        f"{avg_score:.1f}"
                    )
                else:
                    st.metric("Average Score", "N/A")

            with col4:
                st.metric(
                    "Total Conversaciones",
                    progress_data.get("total_conversations", 0)
                )
        else:
            st.error("Unable to load learning statistics.")
else:
    error_msg = student_data.get("error", student_data.get("detail", "Failed to load student data"))
    st.error(f"Error: {error_msg}")

st.divider()

# Tips section
st.subheader("💡 Consejos de aprendizaje")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Cómo mejorar tu nivel de conocimientos:**
    - Interactúa regularmente con el tutor de IA
    - Practica con diferentes tipos de problemas
    - Pide aclaraciones cuando sea necesario
    - Revisar el feedback sobre tus evaluaciones
    """)

with col2:
    st.markdown("""
    **Estrategias de aprendizaje eficaces:**
    - Comienza con los fundamentos antes de abordar temas avanzados
    - Trabaja con ejemplos paso a paso
    - Conecta nuevos conceptos con conocimientos previos
    - Ponte a prueba periódicamente con evaluaciones
    """)

with st.sidebar:
    st.divider()
    if st.button("Logout", key="logout_btn", type="primary"):
        api_client.logout()
        st.switch_page("app.py")
