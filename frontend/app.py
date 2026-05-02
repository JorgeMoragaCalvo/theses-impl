import os

import requests
import streamlit as st
from dotenv import load_dotenv

from utils.activity_tracker import (
    PAGE_HOME,
    flush_events,
    track_chat_message,
    track_interaction,
    track_page_visit,
)
from utils.api_client import get_api_client
from utils.constants import (
    DEFAULT_TOPIC,
    TOPIC_DESCRIPTIONS,
    TOPIC_OPTIONS,
    TOPICS_LIST,
)
from utils.idle_detector import inject_idle_detector
from utils.pages_registry import set_home_page

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Get API client
api_client = get_api_client(BACKEND_URL)

# Store backend URL for activity tracker
if "_backend_url" not in st.session_state:
    st.session_state._backend_url = BACKEND_URL

# Page configuration
st.set_page_config(
    page_title="Tutor de IA - Métodos de optimización",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stButton>button {
        width: 100%;
    }

    /* ── Hero ── */
    .hero-section {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
        border-radius: 16px;
        padding: 3rem 2rem 2.5rem;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero-section::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 70% 30%, rgba(255,255,255,0.08) 0%, transparent 60%);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.18);
        color: #fff;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.35rem 1rem;
        border-radius: 999px;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255,255,255,0.25);
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #fff;
        margin: 0 0 0.8rem;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.85);
        margin: 0 auto 2rem !important;
        max-width: 520px;
        line-height: 1.6;
        text-align: center !important;
    }
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 2.5rem;
        flex-wrap: wrap;
    }
    .hero-stat {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: #fff;
    }
    .hero-stat-value {
        font-size: 1.5rem;
        font-weight: 700;
    }
    .hero-stat-label {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.75);
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-top: 0.1rem;
    }
    .hero-stat-divider {
        width: 1px;
        background: rgba(255,255,255,0.25);
        align-self: stretch;
        margin: 0.3rem 0;
    }

    /* ── Feature cards ── */
    .features-row {
        display: flex;
        gap: 1.2rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }
    .feature-card {
        flex: 1;
        min-width: 220px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 4px solid #6366f1;
        border-radius: 12px;
        padding: 1.4rem 1.2rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(99,102,241,0.18);
    }
    .feature-card:nth-child(2) { border-left-color: #8b5cf6; }
    .feature-card:nth-child(3) { border-left-color: #3b82f6; }
    .feature-card-icon {
        font-size: 2rem;
        margin-bottom: 0.6rem;
    }
    .feature-card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    .feature-card-desc {
        font-size: 0.88rem;
        color: #94a3b8;
        line-height: 1.55;
        margin-bottom: 0.8rem;
    }
    .feature-card-cta {
        font-size: 0.8rem;
        color: #818cf8;
        font-style: italic;
    }

    /* ── Steps ── */
    .steps-section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 1.2rem;
    }
    .steps-row {
        display: flex;
        gap: 1.2rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }
    .step-card {
        flex: 1;
        min-width: 180px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 4px solid #6366f1;
        border-radius: 12px;
        padding: 1.2rem 1rem;
        display: flex;
        align-items: flex-start;
        gap: 0.9rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .step-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(99,102,241,0.18);
    }
    .step-card:nth-child(2) { border-left-color: #8b5cf6; }
    .step-card:nth-child(3) { border-left-color: #3b82f6; }
    .step-number {
        flex-shrink: 0;
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #fff;
        font-size: 1rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .step-body {}
    .step-title {
        font-size: 0.93rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.25rem;
    }
    .step-detail {
        font-size: 0.8rem;
        color: #94a3b8;
        line-height: 1.5;
    }

    /* ── Topic cards ── */
    .topic-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 4px solid #6366f1;
        border-radius: 10px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.9rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .topic-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(99,102,241,0.18);
    }
    .topic-card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #c7d2fe;
        margin-bottom: 0.5rem;
    }
    .topic-card ul {
        margin: 0;
        padding-left: 1.2rem;
    }
    .topic-card li {
        font-size: 0.82rem;
        color: #94a3b8;
        line-height: 1.55;
        margin-bottom: 0.2rem;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 1.2rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

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


def check_backend_health():
    """Check if the backend is available."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"error": str(e)}


# Authentication forms removed - now using the API client


def main():
    """Main application entry point."""

    # Header
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-badge">🎓 Sistema de Tutoría Adaptativa</div>
            <h1 class="hero-title">Domina los Métodos<br>de Optimización</h1>
            <p class="hero-subtitle">
                Tu asistente de IA personalizado para aprender técnicas de optimización
                con retroalimentación instantánea y seguimiento de progreso.
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <span class="hero-stat-value">5</span>
                    <span class="hero-stat-label">Temas</span>
                </div>
                <div class="hero-stat-divider"></div>
                <div class="hero-stat">
                    <span class="hero-stat-value">IA</span>
                    <span class="hero-stat-label">Adaptativa</span>
                </div>
                <div class="hero-stat-divider"></div>
                <div class="hero-stat">
                    <span class="hero-stat-value">⚡</span>
                    <span class="hero-stat-label">Retroalimentación instantánea</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Check backend health
    is_healthy, health_data = check_backend_health()

    # Sidebar - Student Profile
    with st.sidebar:
        st.header("👤 Perfil del estudiante")

        # Backend status indicator
        if is_healthy:
            st.success("✅ Connected to backend")
            if "llm_provider" in health_data:
                st.info(f"🤖 LLM: {health_data['llm_provider']}")
        else:
            st.error("❌ Backend not available")
            st.warning("Please ensure the backend server is running at " + BACKEND_URL)
            st.code("cd backend\nuvicorn app.main:app --reload", language="bash")

        st.divider()

        # Authentication section
        if not api_client.is_authenticated():
            # Show login/register tabs
            auth_tab = st.radio(
                "Elige una acción:", ["Login", "Register"], horizontal=True
            )

            if auth_tab == "Login":
                st.subheader("Login")
                login_email = st.text_input("Email", key="login_email")
                login_password = st.text_input(
                    "Password", type="password", key="login_password"
                )

                if st.button("Login", type="primary", key="login_btn"):
                    if login_email and login_password:
                        with st.spinner("Logging in..."):
                            success, data = api_client.login(
                                login_email, login_password
                            )
                            if success:
                                st.success(
                                    f"Bienvenido de nuevo, {data['user']['name']}!"
                                )
                                st.rerun()
                            else:
                                error_msg = data.get("detail", "Login failed")
                                st.error(f"Error: {error_msg}")
                    else:
                        st.warning("¡Por favor ingresa tu email y contraseña!")

            else:  # Register
                st.subheader("Registro")
                register_name = st.text_input("Nombre", key="register_name")
                register_email = st.text_input("Email", key="register_email")
                register_password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password",
                    help="Minimum 8 characters",
                )
                register_password_confirm = st.text_input(
                    "Confirmar Password",
                    type="password",
                    key="register_password_confirm",
                )

                if st.button("Registro", type="primary", key="register_btn"):
                    if register_name and register_email and register_password:
                        if register_password != register_password_confirm:
                            st.error("¡Las contraseñas no coinciden!")
                        elif len(register_password) < 8:
                            st.error("¡La contraseña debe tener al menos 8 caracteres!")
                        else:
                            with st.spinner("Creando cuenta..."):
                                success, data = api_client.register(
                                    register_name, register_email, register_password
                                )
                                if success:
                                    if data.get("status") == "pending_approval":
                                        st.warning(
                                            f"Cuenta creada para {register_email}. Tu cuenta está pendiente de aprobación por un administrador."
                                        )
                                    else:
                                        st.success(
                                            f"Bienvenido, {data['user']['name']}! Tu cuenta ha sido creada."
                                        )
                                        st.rerun()
                                else:
                                    error_msg = data.get(
                                        "detail", "Registration failed"
                                    )
                                    st.error(f"Error: {error_msg}")
                    else:
                        st.warning("¡Por favor, rellena todos los campos!")

        else:
            # Show logged-in user
            user_name = st.session_state.get("student_name", "User")
            user_email = st.session_state.get("student_email", "")
            user_role = st.session_state.get("user_role", "user")

            st.success(f"Inició sesión como: **{user_name}**")
            st.text(f"Email: {user_email}")
            if user_role == "admin":
                st.info("Rol: Administrador")

            if st.button("Logout", key="logout_btn"):
                flush_events()
                api_client.logout()
                st.success("¡Cierre de sesión exitoso!")
                st.rerun()

            st.divider()

            # Topic selector for logged-in users
            st.subheader("🎯 Seleccionar tema")

            # Initialize the topic in the session state if not present
            if "selected_topic" not in st.session_state:
                st.session_state.selected_topic = DEFAULT_TOPIC

            selected_topic = st.selectbox(
                "Elige tu enfoque de aprendizaje:",
                options=TOPICS_LIST,
                index=TOPICS_LIST.index(st.session_state.selected_topic),
                key="home_topic_selector",
                help="Selecciona el tema de optimización sobre el que deseas aprender",
            )
            st.session_state.selected_topic = selected_topic

        st.divider()

        st.subheader("📚 Temas tratados")
        for topic in TOPICS_LIST:
            st.text(f"• {topic}")

    # Main content area
    if not is_healthy:
        st.error("⚠️ Backend Server Not Available")
        st.markdown("""
            ### How to Start the Backend:

        1. Open a terminal in the project directory
        2. Navigate to backend folder:
        ```bash
        cd backend
        ```

        3. Activate virtual environment:
        ```bash
        # Windows
        venv\\Scripts\\activate

        # macOS/Linux
        source venv/bin/activate
        ```

        4. Run the FastAPI server:
        ```bash
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ```

        5. Refresh this page once the backend is running
        """)
        return

    if not api_client.is_authenticated():
        # Feature cards
        st.markdown(
            """
            <div class="features-row">
                <div class="feature-card">
                    <div class="feature-card-icon">💬</div>
                    <div class="feature-card-title">Chat con IA</div>
                    <div class="feature-card-desc">
                        Interactúa con tutores de IA especializados en cada tema de optimización.
                        Obtén explicaciones adaptadas a tu nivel de conocimiento.
                    </div>
                    <div class="feature-card-cta">→ Haz preguntas y resuelve problemas</div>
                </div>
                <div class="feature-card">
                    <div class="feature-card-icon">📝</div>
                    <div class="feature-card-title">Evaluaciones</div>
                    <div class="feature-card-desc">
                        Pon a prueba tus conocimientos con ejercicios de práctica generados por IA
                        y recibe retroalimentación detallada al instante.
                    </div>
                    <div class="feature-card-cta">→ Comentarios instantáneos y personalizados</div>
                </div>
                <div class="feature-card">
                    <div class="feature-card-icon">📊</div>
                    <div class="feature-card-title">Seguimiento de Progreso</div>
                    <div class="feature-card-desc">
                        Visualiza tu avance en cada tema, identifica áreas de mejora y
                        mantén un historial de tu aprendizaje.
                    </div>
                    <div class="feature-card-cta">→ Ve tu mejora a lo largo del tiempo</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Getting started steps
        st.markdown(
            '<p class="steps-section-title">🚀 Primeros pasos</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="steps-row">
                <div class="step-card">
                    <div class="step-number">1</div>
                    <div class="step-body">
                        <div class="step-title">Regístrate o inicia sesión</div>
                        <div class="step-detail">
                            Crea tu cuenta en la barra lateral o accede con tus credenciales existentes.
                        </div>
                    </div>
                </div>
                <div class="step-card">
                    <div class="step-number">2</div>
                    <div class="step-body">
                        <div class="step-title">Elige tu tema</div>
                        <div class="step-detail">
                            Selecciona el área de optimización que quieres explorar: LP, IP, NLP y más.
                        </div>
                    </div>
                </div>
                <div class="step-card">
                    <div class="step-number">3</div>
                    <div class="step-body">
                        <div class="step-title">Aprende con tu tutor de IA</div>
                        <div class="step-detail">
                            Chatea, realiza evaluaciones y consulta tu progreso desde el menú lateral.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Topics section
        st.markdown(
            '<p class="section-title">📚 Lo que aprenderás</p>', unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        def _topic_card(topic: str) -> str:
            descriptions = TOPIC_DESCRIPTIONS.get(topic, [])
            items = "".join(f"<li>{d}</li>" for d in descriptions)
            return f'<div class="topic-card"><div class="topic-card-title">{topic}</div><ul>{items}</ul></div>'

        with col1:
            for topic in TOPICS_LIST[:3]:
                st.markdown(_topic_card(topic), unsafe_allow_html=True)

        with col2:
            for topic in TOPICS_LIST[3:]:
                st.markdown(_topic_card(topic), unsafe_allow_html=True)

    else:
        # Analytics tracking
        track_page_visit(PAGE_HOME)
        inject_idle_detector(backend_url=BACKEND_URL)

        # Show the main chat interface for logged-in users
        st.markdown("### 💬 Chatea con un tutor de IA")
        st.markdown(
            "¡Haz preguntas sobre un tema relacionado con métodos de optimización!"
        )

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.conversation_id = None

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(
                message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🎓"
            ):
                st.markdown(message["content"])

        if prompt := st.chat_input("Haz una pregunta sobre métodos de optimización..."):
            # Add the user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🎓"):
                with st.spinner("Pensando..."):
                    # Get a selected topic from the session state
                    selected_topic = st.session_state.get(
                        "selected_topic", DEFAULT_TOPIC
                    )
                    topic_value = TOPIC_OPTIONS[selected_topic]

                    # Use authenticated API client
                    success, data = api_client.post(
                        "/chat",
                        json_data={
                            "message": prompt,
                            "conversation_id": st.session_state.conversation_id,
                            "topic": topic_value,
                        },
                    )

                    if success:
                        assistant_message = data["response"]
                        st.session_state.conversation_id = data["conversation_id"]

                        st.markdown(assistant_message)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": assistant_message}
                        )
                        track_chat_message(
                            PAGE_HOME, topic_value, st.session_state.conversation_id
                        )
                    else:
                        error_msg = data.get(
                            "detail", data.get("error", "Failed to get response")
                        )
                        st.error(f"Error: {error_msg}")

        with st.sidebar:
            st.divider()
            if st.session_state.messages:
                if st.button("🗑️ Limpiar Chat"):
                    track_interaction("clear_chat", PAGE_HOME)
                    flush_events()
                    st.session_state.messages = []
                    st.session_state.conversation_id = None
                    st.rerun()


home_page = st.Page(main, title="app", icon="🏠")
set_home_page(home_page)
pg = st.navigation(
    [
        home_page,
        st.Page("pages/1_chat.py", title="chat", icon="💬"),
        st.Page("pages/2_assessment.py", title="evaluación", icon="📝"),
        st.Page("pages/3_progress.py", title="progreso", icon="📊"),
        st.Page("pages/4_admin.py", title="admin", icon="⚙️"),
    ]
)
pg.run()
