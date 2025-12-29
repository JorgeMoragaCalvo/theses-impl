import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import get_api_client
from utils.constants import TOPIC_OPTIONS
"""
Página de evaluación - Problemas de práctica y cuestionarios.
"""

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Get API client
api_client = get_api_client(BACKEND_URL)

st.set_page_config(page_title="Evaluación - Tutor de IA", page_icon="📝", layout="wide")


# Check if the user is authenticated
if not api_client.is_authenticated():
    st.warning("¡Primero inicia sesión desde la página de inicio!")
    st.info("Haga clic en el enlace de la barra lateral para ir a la página de inicio.")
    st.stop()

# Get student_id from the session
student_id = st.session_state.get("student_id")

# ============================================================================
# API HELPER FUNCTIONS
# ============================================================================

def fetch_student_progress(student_id: int) -> Optional[Dict[str, Any]]:
    """Fetch comprehensive student progress metrics."""
    success, data = api_client.get(f"students/{student_id}/progress")
    if not success:
        st.error(f"Error fetching progress: {data.get('error', 'Unknown error')}")
        return None
    return data


def fetch_assessments(student_id: int, topic: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch student assessments, optionally filtered by topic."""
    params = {}
    if topic and topic != "All Topics":
        params["topic"] = topic

    success, data = api_client.get(f"students/{student_id}/assessments", params=params)
    if not success:
        st.error(f"Error fetching assessments: {data.get('error', 'Unknown error')}")
        return []
    return data


def fetch_single_assessment(assessment_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single assessment by ID."""
    success, data = api_client.get(f"assessments/{assessment_id}")
    if not success:
        st.error(f"Error fetching assessment: {data.get('error', 'Unknown error')}")
        return None
    return data


def generate_assessment(topic: str, difficulty: str,
                       conversation_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Generate a new assessment (student_id extracted from token)."""
    payload = {
        "topic": topic,
        "difficulty": difficulty.lower()
    }
    if conversation_id:
        payload["conversation_id"] = str(conversation_id)

    success, data = api_client.post("assessments/generate", json_data=payload)
    if not success:
        st.error(f"Error generating assessment: {data.get('error', 'Unknown error')}")
        return None
    return data


def submit_assessment(assessment_id: int, student_answer: str) -> Optional[Dict[str, Any]]:
    """Submit an answer to an assessment."""
    success, data = api_client.post(
        f"assessments/{assessment_id}/submit",
        json_data={"student_answer": student_answer}
    )
    if not success:
        st.error(f"Error submitting assessment: {data.get('error', 'Unknown error')}")
        return None
    return data


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "current_assessment" not in st.session_state:
    st.session_state.current_assessment = None

if "show_assessment_form" not in st.session_state:
    st.session_state.show_assessment_form = False


# ============================================================================
# MAIN PAGE
# ============================================================================

st.title("📝 Práctica y Evaluación")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Progreso", "📚 Historial de evaluación", "➕ Nueva evaluación"])


# ============================================================================
# TAB 1: PROGRESS DASHBOARD
# ============================================================================

with tab1:
    st.subheader("📊 Tu Progreso")

    progress_data = fetch_student_progress(st.session_state.student_id)

    if progress_data is not None:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Conversaciones totales",
                progress_data.get("total_conversations", 0)
            )

        with col2:
            st.metric(
                "Total de mensajes",
                progress_data.get("total_messages", 0)
            )

        with col3:
            st.metric(
                "Evaluaciones totales",
                progress_data.get("total_assessments", 0)
            )

        with col4:
            avg_score = progress_data.get("average_score")
            if avg_score is not None:
                st.metric(
                    "Puntuación media",
                    f"{avg_score:.1f}",
                    delta=None
                )
            else:
                st.metric("Puntuación media", "N/A")

        st.divider()

        # Knowledge Levels
        knowledge_levels = progress_data.get("knowledge_levels", {})
        if knowledge_levels:
            st.subheader("🎯 Knowledge Levels")
            cols = st.columns(min(3, len(knowledge_levels)))
            for idx, (topic, level) in enumerate(knowledge_levels.items()):
                with cols[idx % 3]:
                    # Color code based on level
                    if level == "beginner":
                        color = "🔵"
                    elif level == "intermediate":
                        color = "🟢"
                    else:
                        color = "🟡"

                    st.markdown(f"{color} **{topic.replace('_', ' ').title()}**: {level.capitalize()}")

        st.divider()

        # Topics Covered
        topics_covered = progress_data.get("topics_covered", [])
        if topics_covered:
            st.subheader("📚 Temas tratados")
            # Display as badges
            topic_html = " ".join([
                f'<span style="background-color: #0d0d0d; padding: 0.3rem 0.7rem; ' # #e0e7ff
                f'border-radius: 1rem; margin: 0.2rem; display: inline-block;">{topic}</span>'
                for topic in topics_covered
            ])
            st.markdown(topic_html, unsafe_allow_html=True)
            st.divider()

        # Recent Activity Timeline
        recent_activity = progress_data.get("recent_activity", [])
        if recent_activity:
            st.subheader("📅 Actividad reciente")

            for activity in recent_activity[:10]:  # Show the last 10 activities
                activity_type = activity.get("type", "unknown")
                timestamp = activity.get("timestamp", "")
                topic = activity.get("topic", "General")

                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    time_str = timestamp

                if activity_type == "conversation":
                    message_count = activity.get("message_count", 0)
                    st.markdown(
                        f"💬 **Conversación** - {topic} - {message_count} mensajes - *{time_str}*"
                    )
                elif activity_type == "assessment":
                    score = activity.get("score")
                    status = activity.get("status", "unknown")

                    status_emoji = {
                        "calificado/a": "✅",
                        "enviado": "📝",
                        "pendiente": "⏳"
                    }.get(status, "❓")

                    score_str = f"Puntaje: {score}" if score is not None else status.capitalize()
                    st.markdown(
                        f"{status_emoji} **Evaluación** - {topic} - {score_str} - *{time_str}*"
                    )
        else:
            st.info("Aún no hay actividad. ¡Inicia una conversación o realiza una evaluación!")
    else:
        st.error("Unable to load progress data.")


# ============================================================================
# TAB 2: ASSESSMENT HISTORY
# ============================================================================

with tab2:
    st.subheader("📚 Historial de evaluación")

    # Topic filter
    col1, col2 = st.columns([3, 1])
    with col1:
        topic_filter = st.selectbox(
            "Filtrar por tema:",
            ["Todos los temas", "Investigación de operaciones", "Modelado matemático",
             "Programación lineal", "Programación entera", "Programación no lineal"],
            key="history_topic_filter"
        )

    with col2:
        if st.button("🔄 Refrescar", key="refresh_history"):
            st.rerun()

    # Convert display name to API enum value
    topic_value = None
    if topic_filter != "All Topics": # Todos los temas
        topic_value = TOPIC_OPTIONS.get(topic_filter, topic_filter.lower().replace(" ", "_"))

    # Fetch assessments
    assessments = fetch_assessments(
        st.session_state.student_id,
        topic=topic_value
    )

    if assessments:
        st.info(f"Encontradas {len(assessments)} evaluacion(es)")

        # Sort by created_at descending
        assessments_sorted = sorted(
            assessments,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )

        for assessment in assessments_sorted:
            assessment_id = assessment.get("id")
            topic = assessment.get("topic", "Unknown")
            question = assessment.get("question", "")
            score = assessment.get("score")
            max_score = assessment.get("max_score", 100)
            feedback = assessment.get("feedback")
            created_at = assessment.get("created_at", "")
            submitted_at = assessment.get("submitted_at")
            graded_at = assessment.get("graded_at")
            student_answer = assessment.get("student_answer")

            # Determine the status with the grading source
            graded_by = assessment.get("graded_by")
            overridden_at = assessment.get("overridden_at")

            if graded_at:
                if overridden_at:
                    status = "✅ Reviewed by Admin"
                    status_color = "green"
                elif graded_by == "admin":
                    status = "✅ Graded by Admin"
                    status_color = "green"
                elif graded_by == "auto":
                    status = "✅ Auto-graded"
                    status_color = "green"
                else:
                    status = "✅ Graded"
                    status_color = "green"
            elif submitted_at:
                status = "📝 Submitted"
                status_color = "blue"
            else:
                status = "⏳ Pending"
                status_color = "orange"

            # Format date
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = created_at

            # Create expander for each assessment
            with st.expander(
                f"{status} - {topic} - {date_str}" +
                (f" - Score: {score}/{max_score}" if score is not None else "")
            ):
                st.markdown(f"**Pregunta:**")
                st.markdown(question)

                if student_answer:
                    st.markdown(f"**Tu respuesta:**")
                    st.info(student_answer)

                if graded_at:
                    # Show grading source indicator
                    if overridden_at:
                        st.info("🔍 **Revisado por el administrador**: la calificación automática original se revisó y actualizó manualmente.")
                    elif graded_by == "auto":
                        st.info("🤖 **Calificación automática** - Calificado/a instantáneamente por la IA")
                    elif graded_by == "admin":
                        st.info("👨‍🏫 ** Calificado/a manualmente ** - Calificado/a por un administrador")

                    if score is not None:
                        percentage = (score / max_score) * 100 if max_score > 0 else 0
                        st.metric("Score", f"{score}/{max_score}", f"{percentage:.1f}%")

                    if feedback:
                        st.markdown(f"**Comentario:**")
                        st.success(feedback)

                    rubric = assessment.get("rubric")
                    if rubric:
                        st.markdown(f"**Rúbrica de calificación:**")
                        st.info(rubric)

                    correct_answer = assessment.get("correct_answer")
                    if correct_answer:
                        st.markdown(f"**Respuesta correcta:**")
                        st.markdown(correct_answer)
                elif submitted_at:
                    st.warning("⏳ Evaluación enviada, pero aún no calificada. Esto es inusual; la calificación debería ser instantánea..")
                else:
                    # Allow submission
                    st.warning("Evaluación aún no enviada.")

                    answer_key = f"answer_{assessment_id}"
                    answer = st.text_area(
                        "Tu respuesta:",
                        key=answer_key,
                        height=150,
                        value=student_answer or ""
                    )

                    if st.button(f"Enviar respuesta", key=f"submit_{assessment_id}"):
                        if answer.strip():
                            result = submit_assessment(assessment_id, answer.strip())
                            if result is not None:
                                st.success("¡Respuesta enviada exitosamente!")
                                st.rerun()
                        else:
                            st.error("Por favor proporcione una respuesta antes de enviar.")
    else:
        st.info("Aún no hay evaluaciones. ¡Genera tu primera evaluación en la pestaña 'Nueva evaluación'!")


# ============================================================================
# TAB 3: NEW ASSESSMENT
# ============================================================================

with tab3:
    st.subheader("➕ Generar nueva evaluación")

    col1, col2 = st.columns(2)

    with col1:
        new_topic = st.selectbox(
            "Select a topic:",
            [
                "Investigación de Operaciones",
                "Modelado Matemático",
                "Programación Lineal",
                "Programación Entera",
                "Programación No Lineal"
            ],
            key="new_topic"
        )

    with col2:
        new_difficulty = st.selectbox(
            "Selecciona dificultad:",
            ["Principiante", "Intermedio", "Avanzado"],
            key="new_difficulty"
        )

    if st.button("Generar evaluación", type="primary", key="generate_btn"):
        with st.spinner("Generando evaluación..."):
            # Convert display name to API enum value
            topic_value = TOPIC_OPTIONS.get(new_topic, new_topic.lower().replace(" ", "_"))
            # student_id extracted from the auth token automatically
            result = generate_assessment(
                topic_value,
                new_difficulty
            )

            if result is not None:
                st.session_state.current_assessment = result
                st.session_state.show_assessment_form = True
                st.success("¡Evaluación generada exitosamente!")
                st.rerun()

    # Display current assessment if available
    if st.session_state.show_assessment_form and st.session_state.current_assessment is not None:
        st.divider()

        current = st.session_state.current_assessment
        assessment_id = current.get("id")
        question = current.get("question", "")
        topic = current.get("topic", "")

        st.subheader(f"📝 Evaluación: {topic}")
        st.markdown("**Pregunta:**")
        st.markdown(question)

        rubric = current.get("rubric")
        if rubric:
            st.markdown("**Rúbrica de calificación:**")
            st.info(rubric)

        # Check if already submitted
        if current.get("submitted_at"):
            st.info("Esta evaluación ya ha sido enviada.")

            if current.get("student_answer"):
                st.markdown("**Tu respuesta:**")
                st.info(current.get("student_answer"))

            if current.get("graded_at"):
                # Show grading source indicator
                graded_by = current.get("graded_by")
                overridden_at = current.get("overridden_at")

                if overridden_at:
                    st.info("🔍 **Reviewed by Admin** - Original auto-grade was manually reviewed and updated")
                elif graded_by == "auto":
                    st.info("🤖 **Automatically Graded** - Graded instantly by AI")
                elif graded_by == "admin":
                    st.info("👨‍🏫 **Manually Graded** - Graded by an administrator")

                score = current.get("score")
                max_score = current.get("max_score", 100)
                feedback = current.get("feedback")

                if score is not None:
                    percentage = (score / max_score) * 100 if max_score > 0 else 0
                    st.metric("Score", f"{score}/{max_score}", f"{percentage:.1f}%")

                if feedback:
                    st.markdown("**Comentario:**")
                    st.success(feedback)
            else:
                st.warning("⏳ Evaluación enviada, pero aún no calificada. Esto es inusual; la calificación debería ser instantánea..")
        else:
            # Answer input
            answer = st.text_area(
                "Tu respuesta:",
                height=200,
                key="current_assessment_answer",
                placeholder="Escribe tu respuesta aquí..."
            )

            col1, col2 = st.columns([1, 4])

            with col1:
                if st.button("Submit", type="primary", key="submit_current"):
                    if answer.strip():
                        result = submit_assessment(assessment_id, answer.strip())
                        if result is not None:
                            st.success("¡Respuesta enviada exitosamente!")
                            st.session_state.current_assessment = result
                            st.rerun()
                    else:
                        st.error("Por favor proporcione una respuesta antes de enviar.")

            with col2:
                if st.button("Cancelar", key="cancel_current"):
                    st.session_state.current_assessment = None
                    st.session_state.show_assessment_form = False
                    st.rerun()


# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption("💡 Tip: ¡Realiza evaluaciones para seguir tu progreso e identificar áreas de mejora!")
