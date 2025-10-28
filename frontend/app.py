import streamlit as st
import requests
from datetime import datetime
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
None