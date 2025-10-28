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

if st.button("Generate Problem", type="primary", disabled=True):
    st.info("This feature will be implemented in Week 4")

st.divider()

# Show placeholder assessment results
st.subheader("📈 Your Recent Assessments")
st.info("No assessments yet. This feature will be available soon!")

with st.expander("Preview: Example Assessment"):
    st.markdown("""
    **Question:** Formulate a linear programming problem for the following scenario:

    A company produces two products A and B. Product A requires 2 hours of labor and 1 kg of material.
    Product B requires 1 hour of labor and 2 kg of material. The company has 100 hours of labor and 80 kg
    of material available. Product A yields a profit of $30 and Product B yields $40. Maximize profit.

    **Your Answer:** *(Will be submitted here)*

    **Correct Answer:**
    ```
    Maximize: Z = 30x₁ + 40x₂
    Subject to:
        2x₁ + x₂ ≤ 100  (labor constraint)
        x₁ + 2x₂ ≤ 80   (material constraint)
        x₁, x₂ ≥ 0      (non-negativity)
    ```

    **Score:** 85/100

    **Feedback:** Your formulation was mostly correct! The objective function and constraints
    were properly identified. Remember to always explicitly state the non-negativity constraints.
    """)