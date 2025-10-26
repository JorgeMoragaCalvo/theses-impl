from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from .config import settings
from .app.database import get_db, init_db, Student, Conversation, Message, Assessment, Feedback
from .models import (HealthResponse, StudentCreate, StudentResponse, StudentUpdate,
                     ChatRequest, ChatResponse, ConversationResponse, MessageResponse, FeedbackCreate,
                     FeedbackResponse, ProgressResponse)

