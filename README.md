# Project Overview

---
<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.120%2B-009485?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![LangChain](https://img.shields.io/badge/LangChain-1.0%2B-1c3c3c?style=flat-square&logo=langchain&logoColor=white)](https://www.langchain.com/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.50%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/) [![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8%2B-11557C?style=flat-square&logo=matplotlib&logoColor=white)](https://matplotlib.org/) [![Pandas](https://img.shields.io/badge/Pandas-2.3%2B-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

[![ChatGPT](https://custom-icon-badges.demolab.com/badge/ChatGPT-74aa9c?logo=openai&logoColor=white)](#) [![Claude](https://img.shields.io/badge/Claude-D97757?logo=claude&logoColor=fff)](#) [![Google Gemini](https://img.shields.io/badge/Google%20Gemini-886FBF?logo=googlegemini&logoColor=fff)](#)
</div>

<div align="center">

📚 **Massive Document Knowledge Q&A** &nbsp;•&nbsp; 🎨 **Interactive Learning Visualization**<br>
🎯 **Knowledge Reinforcement** &nbsp;•&nbsp; 🔍 **Deep Research & Idea Generation**

</div>

---

## Key Features
### 📚 Massive Document Knowledge Q&A

### 🎨 Interactive Learning Visualization

### 🎯 Knowledge Reinforcement

### 🔍 Deep Research & Idea Generation

## 📋 Todo
### Overview

5-phase implementation to improve pedagogical effectiveness from Level 3/5 to Level 4–5/5 maturity.

[TODO Details](docs/notes/todo-details.md). (Pedagogical Improvements Implementation Plan)

---

#### Phase 1: Competency Framework & Mastery Tracking

##### 1.1 Database Models

**File:** `backend/app/database.py`

##### 1.2 Concept Taxonomy Files

- **Create:** `data/concept_taxonomies/linear_programming.json`
- **Create:** `data/concept_taxonomies/mathematical_modeling.json`
- **Create:** `data/concept_taxonomies/integer_programming.json`

##### 1.3 New Service

**Create:** `backend/app/services/competency_service.py`

##### 1.4 Integration

**Modify:** `backend/app/services/grading_service.py`

- Add to grading prompt: `"concepts_tested": ["lp.formulation.variables", ...]`
- After grading, call `competency_service.update_competency()`

**Modify:** `backend/app/services/conversation_service.py`

- Add `get_student_competency_context()` method
- Include mastery data in the agent context

##### 1.5 API Endpoints

**Modify:** `backend/app/main.py`

---

#### Phase 2: Error Taxonomy & Targeted Remediation

##### 2.1 Error Taxonomy Files

**Create:** `data/error_taxonomies/mathematical_modeling.json`

##### 2.2 Database Model

**Modify:** `backend/app/database.py`

##### 2.3 Enhanced Grading

**Modify:** `backend/app/services/grading_service.py`

##### 2.4 New Service

**Create:** `backend/app/services/remediation_service.py`

##### 2.5 Agent Integration

**Modify:** `backend/app/agents/base_agent.py`

---

#### Phase 3: Spaced Repetition System

##### 3.1 New Service (SM-2 Algorithm)

**Create:** `backend/app/services/spaced_repetition_service.py`

##### 3.2 Database Model

**Modify:** `backend/app/database.py`

##### 3.3 API Endpoints

**Modify:** `backend/app/main.py`

##### 3.4 Agent Integration

**Modify:** `backend/app/agents/base_agent.py`

---

#### Phase 4: Higher-Order Learning Tasks

##### 4.1 Task Type Enums

**Modify:** `backend/app/database.py`

**Modify Assessment model:**

##### 4.2 Task Templates

**Create:** `data/task_templates/higher_order_tasks.json`

##### 4.3 Enhanced Assessment Service

**Modify:** `backend/app/services/assessment_service.py`

##### 4.4 Specialized Grading

**Modify:** `backend/app/services/grading_service.py`

##### 4.5 API Endpoint

**Modify:** `backend/app/main.py`

```python
POST /assessments/generate/higher-order
```

---

#### Phase 5: Metacognitive Scaffolding

##### 5.1 Metacognitive Prompts

**Create:** `data/metacognitive/prompts.json`

##### 5.2 Database Model

**Modify:** `backend/app/database.py`

##### 5.3 New Service

**Create:** `backend/app/services/metacognitive_service.py`

##### 5.4 Agent Integration

**Modify:** `backend/app/agents/base_agent.py`

##### 5.5 API Endpoints

**Modify:** `backend/app/main.py`

##### 5.6 Pydantic Models

**Modify:** `backend/app/models.py`

#### Files Summary

##### New Files to Create:

| File                                                | Purpose                       |
|-----------------------------------------------------|-------------------------------|
| `backend/app/services/competency_service.py`        | Mastery tracking              |
| `backend/app/services/remediation_service.py`       | Error-targeted remediation    |
| `backend/app/services/spaced_repetition_service.py` | SM-2 algorithm                |
| `backend/app/services/metacognitive_service.py`     | Self-assessment tracking      |
| `data/concept_taxonomies/*.json`                    | Concept hierarchies per topic |
| `data/error_taxonomies/*.json`                      | Common errors per topic       |
| `data/task_templates/higher_order_tasks.json`       | Bloom's higher levels         |
| `data/metacognitive/prompts.json`                   | Reflection prompts            |

##### Files to Modify:

| File                                           | Changes                                                |
|------------------------------------------------|--------------------------------------------------------|
| `backend/app/database.py`                      | 5 new models + 2 enums                                 |
| `backend/app/models.py`                        | 8+ new Pydantic schemas                                |
| `backend/app/main.py`                          | 10+ new API endpoints                                  |
| `backend/app/services/grading_service.py`      | Concept extraction, error classification               |
| `backend/app/services/assessment_service.py`   | Higher-order task generation                           |
| `backend/app/services/conversation_service.py` | Competency context                                     |
| `backend/app/agents/base_agent.py`             | Error context, metacognitive prompts, review reminders |

---

#### Implementation Order

```diagram
Phase 1 (Competency) ──┬── Phase 2 (Errors) ──┐
                       │                       │
                       ├── Phase 3 (SRS) ──────┼── Integration
                       │                       │
Phase 4 (Higher-Order)─┴── Phase 5 (Meta) ────┘
```

**Recommended sequence:**

1. **Phase 1** – Foundation for all tracking
2. **Phase 4** – Independent, high pedagogical value
3. **Phase 2** – Builds on Phase 1 concepts
4. **Phase 5** – Can start after Phase 1
5. **Phase 3** – Depends on Phase 1 completion

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
