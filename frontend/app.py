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
