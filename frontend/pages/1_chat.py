import requests
import os
from dotenv import load_dotenv
"""
Chat page - Detailed conversation interface with topic selection.
"""

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")