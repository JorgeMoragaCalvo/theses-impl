# Project Overview

---
<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.120%2B-009485?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![LangChain](https://img.shields.io/badge/LangChain-1.0%2B-1c3c3c?style=flat-square&logo=langchain&logoColor=white)](https://www.langchain.com/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.50%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/) [![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8%2B-11557C?style=flat-square&logo=matplotlib&logoColor=white)](https://matplotlib.org/) [![Pandas](https://img.shields.io/badge/Pandas-2.3%2B-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

[![ChatGPT](https://custom-icon-badges.demolab.com/badge/ChatGPT-74aa9c?logo=openai&logoColor=white)](#) [![Claude](https://img.shields.io/badge/Claude-D97757?logo=claude&logoColor=fff)](#) [![Google Gemini](https://img.shields.io/badge/Google%20Gemini-886FBF?logo=googlegemini&logoColor=fff)](#)
</div>

<div align="center">

🤖 **Multi-agent tutoring system** &nbsp;•&nbsp; 💬 **Conversational learning interface**<br>
🔄 **Adaptive learning** &nbsp;•&nbsp; 📝 **Assessment Service** &nbsp;•&nbsp; 📊 **Student progress tracking and metrics**<br>
👥 **User management and authentication**

</div>

---

## Key Features
### 🤖 Multi-agent tutoring system

### 💬 Conversational learning interface

### 🔄 Adaptive learning characteristics

### 📝 Assessment system

### 📊 Student progress tracking and metrics

### 👥 User management and authentication

## 📋 Todo
### Overview

5-phase implementation to improve pedagogical effectiveness from Level 3/5 to Level 4–5/5 maturity.

[TODO Details](docs/notes/todo-details.md). (Pedagogical Improvements Implementation Plan)

---

## 🚀 Getting Started

### Backend Architectural Patterns Summary           
                                  
The backend follows a Layered Architecture with Service-Oriented Design. Here are the key patterns identified:                                                                    
                                                                                                                                                                                    
#### Overall Structure                                                                                                                                                                 
                                                                                                                                                                                    
API Layer (FastAPI) → Business Logic (Services/Agents) → Data Access (SQLAlchemy) → PostgreSQL                                                                                    

#### Design Patterns Found

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

The frontend is built with Streamlit (Python), not a traditional JS framework. This enables full-stack Python development.                                                        
                                                                                                                                                                                    
#### Overall Structure                                                                                                                                                                 
```diagram                                                                                                                                                                                    
Streamlit Multi-Page Application (MPA)
├── app.py          → Home/Auth page
├── pages/1_chat.py → Chat interface
├── pages/2_assessment.py → Assessment/practice
├── pages/3_progress.py   → Progress tracking
└── pages/4_admin.py      → Admin dashboard
```

#### Key Patterns Identified

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
