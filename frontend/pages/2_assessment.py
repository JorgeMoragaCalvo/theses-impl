import streamlit as st
import os
from dotenv import load_dotenv
"""
Assessment page - Practice problems and quizzes.
"""

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Assessment - AI Tutor", page_icon="📝", layout="wide")
st.title("📝 Practice & Assessment")

# Check if the student is logged in
if "student_id" not in st.session_state or st.session_state.student_id is None:
    st.warning("Please login from the home page first!")
    st.stop()

st.info("🚧 Assessment features coming soon in Week 4!")

st.markdown("""
### Planned Features:

#### 🎯 Practice Problems
- AI-generated practice problems based on your knowledge level
- Step-by-step hints and guidance
- Instant feedback on your solutions

#### 📊 Quizzes
- Topic-specific quizzes
- Adaptive difficulty based on performance
- Detailed explanations for incorrect answers

#### 🏆 Progress Tracking
- Track your scores over time
- Identify areas that need more practice
- Earn achievements for milestones
""")

st.divider()
st.subheader("🔜 Coming Soon: Generate Practice Problem")

col1, col2 = st.columns(2)

with col1:
    topic = st.selectbox(
        "Select a topic:",
        [
            "Operations Research",
            "Mathematical Modeling",
            "Linear Programming",
            "Integer Programming",
            "Nonlinear Programming"
        ]
    )

with col2:
    difficulty = st.selectbox(
        "Select difficulty:",
        ["Beginner", "Intermediate", "Advanced"]
    )