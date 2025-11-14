import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.api_client import get_api_client
from utils.constants import TOPIC_OPTIONS, TOPICS_LIST, TOPIC_DESCRIPTIONS, DEFAULT_TOPIC
"""
Main application page - AI Tutor for Optimization Methods.
"""

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Get API client
api_client = get_api_client(BACKEND_URL)

# Page configuration
st.set_page_config(
    page_title="AI Tutor - Optimization Methods",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

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
    st.markdown('<p class="main-header">🎓 AI Tutor for Optimization Methods</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Your personalized assistant for learning optimization techniques</p>',
        unsafe_allow_html=True
    )

    # Check backend health
    is_healthy, health_data = check_backend_health()

    # Sidebar - Student Profile
    with st.sidebar:
        st.header("👤 Student Profile")

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
            auth_tab = st.radio("Choose action:", ["Login", "Register"], horizontal=True)

            if auth_tab == "Login":
                st.subheader("Login")
                login_email = st.text_input("Email", key="login_email")
                login_password = st.text_input("Password", type="password", key="login_password")

                if st.button("Login", type="primary", key="login_btn"):
                    if login_email and login_password:
                        with st.spinner("Logging in..."):
                            success, data = api_client.login(login_email, login_password)
                            if success:
                                st.success(f"Welcome back, {data['user']['name']}!")
                                st.rerun()
                            else:
                                error_msg = data.get("detail", "Login failed")
                                st.error(f"Error: {error_msg}")
                    else:
                        st.warning("Please enter your email and password!")

            else:  # Register
                st.subheader("Register")
                register_name = st.text_input("Name", key="register_name")
                register_email = st.text_input("Email", key="register_email")
                register_password = st.text_input("Password", type="password", key="register_password", help="Minimum 8 characters")
                register_password_confirm = st.text_input("Confirm Password", type="password", key="register_password_confirm")

                if st.button("Register", type="primary", key="register_btn"):
                    if register_name and register_email and register_password:
                        if register_password != register_password_confirm:
                            st.error("Passwords do not match!")
                        elif len(register_password) < 8:
                            st.error("Password must be at least 8 characters!")
                        else:
                            with st.spinner("Creating account..."):
                                success, data = api_client.register(register_name, register_email, register_password)
                                if success:
                                    st.success(f"Welcome, {data['user']['name']}! Your account has been created.")
                                    st.rerun()
                                else:
                                    error_msg = data.get("detail", "Registration failed")
                                    st.error(f"Error: {error_msg}")
                    else:
                        st.warning("Please fill in all fields!")

        else:
            # Show logged-in user
            user_name = st.session_state.get("student_name", "User")
            user_email = st.session_state.get("student_email", "")
            user_role = st.session_state.get("user_role", "user")

            st.success(f"Logged in as: **{user_name}**")
            st.text(f"Email: {user_email}")
            if user_role == "admin":
                st.info("Role: Administrator")

            if st.button("Logout", key="logout_btn"):
                api_client.logout()
                st.success("Logged out successfully!")
                st.rerun()

            st.divider()

            # Topic selector for logged-in users
            st.subheader("🎯 Select Topic")

            # Initialize the topic in the session state if not present
            if "selected_topic" not in st.session_state:
                st.session_state.selected_topic = DEFAULT_TOPIC

            selected_topic = st.selectbox(
                "Choose your learning focus:",
                options=TOPICS_LIST,
                index=TOPICS_LIST.index(st.session_state.selected_topic),
                key="home_topic_selector",
                help="Select which optimization topic you want to learn about"
            )
            st.session_state.selected_topic = selected_topic

        st.divider()

        st.subheader("📚 Topics Covered")
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
        # Welcome screen
        st.markdown("### Welcome to the AI Tutoring System! 👋")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 💬 Chat")
            st.write("Interact with AI tutors specialized in different optimization topics")
            st.info("Ask questions, get explanations, and work through problems")
        with col2:
            st.markdown("#### 📝 Assessments")
            st.write("Test your knowledge with AI-generated practice problems")
            st.info("Get instant feedback and personalized suggestions")
        with col3:
            st.markdown("#### 📊 Progress")
            st.write("Track your learning journey across all topics")
            st.info("See your improvement and indentify areas to focus on")

        st.divider()

        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        1. **Login or Register** in the sidebar to access your account
           - New users: Click 'Register' and create an account
           - Existing users: Click 'Login' with your credentials
        2. **Start learning** with AI tutors
        3. **Navigate to pages** using the sidebar menu:
           - **Chat**: Talk with AI tutors about optimization methods
           - **Assessment**: Take practice quizzes and get instant feedback
           - **Progress**: View your learning statistics and improvement
           - **Admin** (admins only): Manage users and view system stats
        """)
        st.divider()

        st.markdown("### 📚 What You'll Learn")

        col1, col2 = st.columns(2)

        # First column: first 3 topics
        with col1:
            for topic in TOPICS_LIST[:3]:
                descriptions = TOPIC_DESCRIPTIONS.get(topic, [])
                st.markdown(f"**{topic}**")
                for desc in descriptions:
                    st.markdown(f"- {desc}")
                st.markdown("")  # Add spacing

        # Second column: remaining topics
        with col2:
            for topic in TOPICS_LIST[3:]:
                descriptions = TOPIC_DESCRIPTIONS.get(topic, [])
                st.markdown(f"**{topic}**")
                for desc in descriptions:
                    st.markdown(f"- {desc}")
                st.markdown("")  # Add spacing

    else:
        # Show the main chat interface for logged-in users
        st.markdown(f"### 💬 Chat with AI Tutor")
        st.markdown("Ask questions about any optimization method topic!")

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.conversation_id = None

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question about optimization methods..."):
            # Add the user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Get selected topic from session state
                    selected_topic = st.session_state.get("selected_topic", DEFAULT_TOPIC)
                    topic_value = TOPIC_OPTIONS[selected_topic]

                    # Use authenticated API client
                    success, data = api_client.post("/chat", json_data={
                        "message": prompt,
                        "conversation_id": st.session_state.conversation_id,
                        "topic": topic_value
                    })

                    if success:
                        assistant_message = data["response"]
                        st.session_state.conversation_id = data["conversation_id"]

                        st.markdown(assistant_message)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_message
                        })
                    else:
                        error_msg = data.get("detail", data.get("error", "Failed to get response"))
                        st.error(f"Error: {error_msg}")

        with st.sidebar:
            st.divider()
            if st.session_state.messages:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.messages = []
                    st.session_state.conversation_id = None
                    st.rerun()

if __name__ == "__main__":
    main()
