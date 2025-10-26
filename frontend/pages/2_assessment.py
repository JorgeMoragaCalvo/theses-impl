import os
from dotenv import load_dotenv
"""
Assessment page - Practice problems and quizzes.
"""

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")