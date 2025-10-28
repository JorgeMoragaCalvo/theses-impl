import streamlit as st
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
"""
Progress tracking page - Student learning analytics
"""

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Progress - AI Tutor", page_icon="📊", layout="wide")

st.title("📊 Your learning progress")

if "student_id" not in st.session_state or st.session_state.student_id is None:
    st.warning("Please login from the home page first!")
    st.stop()

# Fetch student data
try:
    response = requests.get(f"{BACKEND_URL}/students/{st.session_state.student_id}")
    if response.status_code == 200:
        student_data = response.json()

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
        st.subheader("🎯 Knowledge Levels by Topic")

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

        # Fetch conversations
        try:
            conv_response = requests.get(f"{BACKEND_URL}/students/{st.session_state.student_id}/conversations")
            if conv_response.status_code == 200:
                conversations = conv_response.json()

                st.subheader("💬 Conversation History")
                if conversations:
                    st.metric("Total Conversations", len(conversations))

                    # Show recent conversations
                    st.markdown("#### Recent Conversations")

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
                            if st.button(f"View Details", key=f"view_{conv['id']}"):
                                detail_response = requests.get(f"{BACKEND_URL}/conversations/{conv['id']}")
                                if detail_response.status_code == 200:
                                    detail_data = detail_response.json()
                                    st.write(f"**Messages** {len(detail_data.get('messages', []))}:")
                else:
                    st.info("No conversations yet.")
        except Exception as e:
            st.error(f"Failed to load conversations: {e}")

        st.divider()

        # Placeholder for future metrics
        st.subheader("📈 Learning Statistics")
        st.info("🚧 Detailed statistics coming in Week 3-4!")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Messages", "-", help="Coming soon")
        with col2:
            st.metric("Practice Problems", "-", help="Coming soon")
        with col3:
            st.metric("Average Score", "-", help="Coming soon")
        with col4:
            st.metric("Study Time", "-", help="Coming soon")
    else:
        st.error("Failed to load student data.")
except Exception as e:
    st.error(f"Error loading progress data: {e}")

st.divider()

# Tips section
st.subheader("💡 Learning Tips")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **How to Improve Your Knowledge Level:**
    - Engage regularly with the AI tutor
    - Practice with different types of problems
    - Ask for clarification when needed
    - Review feedback on your assessments
    """)

with col2:
    st.markdown("""
    **Effective Learning Strategies:**
    - Start with fundamentals before advanced topics
    - Work through examples step-by-step
    - Connect new concepts to previous knowledge
    - Test yourself regularly with assessments
    """)