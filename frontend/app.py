import streamlit as st
import requests
import os
from dotenv import load_dotenv
"""
Progress tracking page - Student learning analytics.
"""

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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

def get_or_create_student(name: str, email: str):
    """Get or create the student profile."""
    try:
        # Try to get student by email (we'll implement search later)
        # For now, just create a new student
        response = requests.post(
            f"{BACKEND_URL}/students",
            json={
                "name": name,
                "email": email
            }
        )
        if response.status_code == 201:
            return response.json()
        elif response.status_code == 400:
            # Student exists, we need to fetch by email
            # For now, return None and handle in UI
            return None
    except Exception as e:
        st.error(f"Error creating student: {e}")
        return None

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

        # Initialize session state for the student
        if "student_id" not in st.session_state:
            st.session_state.student_id = None
            st.session_state.student_name = ""
            st.session_state.student_email = ""

        # Student login/registration
        if st.session_state.student_id is None:
            st.subheader("Login / Register")

            name = st.text_input("Name", key="input_name")
            email = st.text_input("Email", key="input_email")

            if st.button("Start learning", type="primary"):
                if name and email:
                    student_data = get_or_create_student(name, email)
                    if student_data:
                        st.session_state.student_id = student_data["id"]
                        st.session_state.student_name = student_data["name"]
                        st.session_state.student_email = student_data["email"]
                        st.success(f"Welcome, {name}!")
                        st.rerun()
                    else:
                        st.warning("Email already exists. We'll implement login soon!")
                else:
                    st.warning("Please enter your name and email!")
        else:
            # Show logged in the student
            st.success(f"Logged in as: **{st.session_state.student_name}**")
            st.text(f"Email: {st.session_state.student_email}")

            if st.button("Logout"):
                st.session_state.student_id = None
                st.session_state.student_name = ""
                st.session_state.student_email = ""
                st.rerun()

        st.divider()

        st.subheader("📚 Topics Covered")
        topics = [
            "Operations Research",
            "Mathematical Modeling",
            "Linear Programming",
            "Integer Programming",
            "Nonlinear Programming"
        ]
        for topic in topics:
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

    if st.session_state.student_id is None:
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
        1. **Enter your name and email** in the sidebar to create your profile
        2. **Click 'Start Learning'** to begin
        3. **Navigate to pages** using the sidebar menu:
           - **Chat**: Talk with AI tutors about optimization methods
           - **Assessment**: Take practice quizzes
           - **Progress**: View your learning statistics
        """)
        st.divider()

        st.markdown("### 📚 What You'll Learn")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Operations Research**
            - Introduction to optimization
            - Problem formulation basics
            - Decision-making frameworks

            **Mathematical Modeling**
            - Translating real problems to math
            - Variable and constraint identification
            - Objective function design

            **Linear Programming**
            - LP formulation and solution
            - Simplex method
            - Duality theory
            """)

        with col2:
            st.markdown("""
            **Integer Programming**
            - Binary and integer variables
            - Branch and bound methods
            - Combinatorial optimization

            **Nonlinear Programming**
            - Unconstrained optimization
            - Constrained optimization
            - KKT conditions
            - Gradient methods
            """)

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
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/chat",
                            json={
                                "student_id": st.session_state.student_id,
                                "message": prompt,
                                "conversation_id": st.session_state.conversation_id
                            }
                        )

                        if response.status_code == 200:
                            data = response.json()
                            assistant_message = data["response"]
                            st.session_state.conversation_id = data["conversation_id"]

                            st.markdown(assistant_message)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": assistant_message
                            })
                        else:
                            st.error(f"Error: {response.status_code}")
                            st.json(response.json())
                    except Exception as e:
                        st.error(f"Failed to get response: {e}")

        with st.sidebar:
            st.divider()
            if st.session_state.messages:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.messages = []
                    st.session_state.conversation_id = None
                    st.rerun()

if __name__ == "__main__":
    main()
