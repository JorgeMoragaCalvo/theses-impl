<div align="center">

# Multi-agent-tutor

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.120%2B-009485?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![LangChain](https://img.shields.io/badge/LangChain-1.0%2B-1c3c3c?style=flat-square&logo=langchain&logoColor=white)](https://www.langchain.com/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.50%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/) [![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8%2B-11557C?style=flat-square&logo=matplotlib&logoColor=white)](https://matplotlib.org/) [![Pandas](https://img.shields.io/badge/Pandas-2.3%2B-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

[![ChatGPT](https://custom-icon-badges.demolab.com/badge/ChatGPT-74aa9c?logo=openai&logoColor=white)](#) [![Claude](https://img.shields.io/badge/Claude-D97757?logo=claude&logoColor=fff)](#) [![Google Gemini](https://img.shields.io/badge/Google%20Gemini-886FBF?logo=googlegemini&logoColor=fff)](#)
</div>

<div align="center">

🤖 **Multi-agent tutoring system** &nbsp;•&nbsp; 💬 **Conversational learning interface**<br>
🔄 **Adaptive learning** &nbsp;•&nbsp; 📝 **Assessment Service** &nbsp;•&nbsp; 📊 **Student progress tracking and metrics**<br>
👥 **User management and authentication**

</div>

---

An adaptive, multi-agent AI tutoring system that provides personalized conversational learning for advanced mathematics and operations research topics. Designed for students and educators to master complex concepts through interactive dialogue and tailored assessments

## Key Features
### 🤖 Multi-agent tutoring system
Multi-agent tutoring system with five AI agents specializing in:
- Operations Research
- Mathematical Modeling
- Linear Programming
- Integer Programming
- Nonlinear Programming

### 💬 Conversational learning interface
- Context-aware responses that use students' conversation history. 
- The system leverages a multi-agent system with a tutor agent that learns from students' interactions. 
- The tutor agent is able to adapt to students' needs and provide personalized responses.

### 🔄 Adaptive learning characteristics
- Detecting confusion through keyword analysis. 
- Alternative explanations when confusion is detected.

### 📝 Assessment system
- Context-aware, using the student's knowledge level and conversation history.
- Three difficulty levels: beginner, intermediate, and advanced.
- Generates detailed feedback for each exercise submission.

### 📊 Student progress tracking and metrics

### 👥 User management and authentication

## 📋 Todo
### Overview

5-phase implementation to improve pedagogical effectiveness from Level 3/5 to Level 4–5/5 maturity.

[TODO Details](docs/notes/todo-details.md). (Pedagogical Improvements Implementation Plan)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL 16+
- An LLM API key (Google Gemini, OpenAI, or Anthropic)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/JorgeMoragaCalvo/theses-impl.git
cd theses-impl
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` and fill in the required values:
- `DATABASE_URL` — PostgreSQL connection string
- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `LLM_PROVIDER` — `gemini` (default), `openai`, or `anthropic`
- The corresponding API key (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY`)

5. Initialize the database:

```bash
python backend/init_db.py
```

### Running (Local Development)

Start the backend and frontend in separate terminals:

**Backend (FastAPI):**

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` (docs at `/docs`).

**Frontend (Streamlit):**

```bash
cd frontend
streamlit run app.py
```

The UI will be available at `http://localhost:8501`.

### Running (Docker Compose)

For a production-like setup with PostgreSQL, Nginx reverse proxy, and HTTPS:

```bash
# Generate self-signed SSL certs (or provide your own in nginx/ssl/)
bash nginx/ssl/generate-certs.sh

# Copy and configure environment
cp .env.example .env
# Edit .env with your values

# Build and start all services
docker compose up --build
```

This starts four services: **PostgreSQL** → **Backend** → **Frontend** → **Nginx** (ports 80/443).

---

## 🏗️ Architecture

### Backend Architectural Patterns Summary
                                  
The backend follows a Layered Architecture with Service-Oriented Design. Here are the key patterns:                                                                    
                                                                                                                                                                                    
#### Overall Structure                                                                                                                                                                 
                                                                                                                                                                                    
API Layer (FastAPI) → Business Logic (Services/Agents) → Data Access (SQLAlchemy) → PostgreSQL                                                                                    

#### Design Patterns

| Pattern              | Location                                      | Purpose                                                                         |
|----------------------|-----------------------------------------------|---------------------------------------------------------------------------------|
| Template Method      | agents/base_agent.py                          | Abstract base agent with get_system_prompt() implemented by subclasses          |
| Factory/Registry     | main.py:79-110                                | AGENT_REGISTRY maps topics to agent getter functions                            |
| Strategy             | base_agent.py:304-359                         | Multiple explanation strategies (step-by-step, example-based, conceptual, etc.) |
| Dependency Injection | Throughout                                    | FastAPI Depends() for db sessions,services                                      |
| Adapter              | services/llm_service.py                       | Unified interface for Gemini/OpenAI/Anthropic providers                         |
| DTO                  | models.py                                     | Pydantic request/response validation                                            |
| Registry             | services/exercise_assessment_service.py:27-84 | ExerciseRegistry auto-discovers exercises                                       |

####  API Design

- RESTful resource-based endpoints
- JWT-based authentication (auth.py)
- Role-based authorization (USER/ADMIN)
- Pydantic validation on all inputs/outputs

#### Database Patterns

- SQLAlchemy ORM with declarative base
- JSON columns for flexible metadata (knowledge_levels, extra_data)
- Audit fields (created_at, updated_at, timestamps)
- Enum handling for topics and grading sources

#### Middleware

- CORS middleware (main.py:143-150)
- Lifespan context manager for startup/shutdown
- Adaptive learning injection in agents (confusion detection, strategy selection)

#### Multi-Agent System
Specialized tutor agents in agents/ inherit from BaseAgent:
- LinearProgrammingAgent
- IntegerProgrammingAgent
- NonlinearProgrammingAgent
- MathematicalModelingAgent
- OperationsResearchAgent

### Frontend Patterns Summary

The frontend is built with Streamlit (Python). This enables full-stack Python development.

#### Overall Structure
```diagram
Streamlit Multi-Page Application (MPA)
├── app.py          → Home/Auth page
├── pages/1_chat.py → Chat interface
├── pages/2_assessment.py → Assessment/practice
├── pages/3_progress.py   → Progress tracking
└── pages/4_admin.py      → Admin dashboard
```

#### Key Patterns

| Aspect           | Pattern                                     | Location                    |
|------------------|---------------------------------------------|-----------------------------|
| Architecture     | Multi-page application (MPA)                | pages/ directory            |
| Organization     | Feature-based + utilities                   | pages/ + utils/             |
| State Management | Streamlit st.session_state                  | All pages                   |
| Routing          | File-based automatic routing                | Numeric prefix in filenames |
| API Client       | Singleton pattern with centralized requests | utils/api_client.py         |
| Authentication   | JWT token + localStorage persistence        | api_client.py, app.py       |
| Styling          | Inline CSS via st.markdown()                | app.py:37-56                |
| Forms            | Imperative with session state               | All pages                   |
  
#### API Client Pattern (utils/api_client.py)

- Singleton instantiation via get_api_client()
- Automatic JWT injection in request headers
- Centralized error handling (401 → auto-logout)
- Methods: get(), post(), put(), delete(), login(), register()

####  State Management

Key session state variables:
- access_token – JWT authentication
- user, student_id, user_role – User profile
- messages, conversation_id – Chat history
- current_assessment – Active assessment
- api_client – Singleton instance

#### Authentication Flow

```diagram
Login/Register → Backend returns JWT → Stored in session_state + localStorage
               → Auto-injected in API headers → 401 triggers auto-logout
```

#### Role-Based Access Control

- api_client.is_authenticated() – Auth check
- api_client.is_admin() - Admin role check
- Page-level guards: if not authenticated: st.stop()

####  Special Features

- Backend health monitoring – check_backend_health()
- Tab-based UI - Assessment (three tabs), Admin (three tabs)
- Spanish language UI – All strings in Spanish
- Conversation persistence – Track conversation ID across sessions

#### Technology Stack

- Streamlit 1.x | Python 3.10+ | requests | python-dotenv | pandas | JWT
