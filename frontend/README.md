# Frontend - AI Tutor Application

## Overview

This is the frontend module for the AI Tutor application, built with **Streamlit**. It provides a web-based interface for students to learn optimization methods through interactive chat, assessments, and progress tracking.

The application specializes in teaching:
- Operations Research (Investigación de Operaciones)
- Mathematical Modeling (Modelado Matemático)
- Linear Programming (Programación Lineal)
- Integer Programming (Programación Entera)
- Nonlinear Programming (Programación No Lineal)

## File Structure

```diagram
frontend/
├── __init__.py          # Python package marker
├── app.py               # Main application entry point (Home page)
├── pages/               # Streamlit multi-page modules
│   ├── __init__.py
│   ├── 1_chat.py        # Chat interface page
│   ├── 2_assessment.py  # Assessment and practice page
│   ├── 3_progress.py    # Progress tracking page
│   └── 4_admin.py       # Admin dashboard page
└── utils/               # Utility modules
    ├── __init__.py
    ├── api_client.py    # HTTP client with authentication
    └── constants.py     # Shared constants and topic definitions
```

## Installation & Setup

### Prerequisites
- Python 3.10+
- Backend API running (default: `http://localhost:8000`)

### Environment Variables
Create a `.env` file or set the following:
```bash
BACKEND_URL=http://localhost:8000  # Backend API URL
```

### Running the Application
```bash
cd frontend
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

## Architecture

```digram
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐        │
│  │  Home   │  │  Chat   │  │Assessment│  │ Progress│        │
│  │ (app)   │  │ (page)  │  │  (page)  │  │ (page)  │        │
│  └────┬────┘  └────┬────┘  └────┬─────┘  └────┬────┘        │
│       │            │            │             │             │
│       └────────────┴─────┬──────┴─────────────┘             │
│                          │                                  │
│                   ┌──────┴──────┐                           │
│                   │  APIClient  │                           │
│                   │  (utils)    │                           │
│                   └──────┬──────┘                           │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTP/REST
                           ▼
                    ┌──────────────┐
                    │   Backend    │
                    │   FastAPI    │
                    └──────────────┘
```

## Business Logic

### 1. Authentication Flow

```diagram
User Registration/Login
        │
        ▼
┌─────────────────────┐
│ APIClient.login()   │
│ APIClient.register()│
└─────────┬───────────┘
          │
          ▼
┌───────────────────┐
│ JWT Token Received│
└─────────┬─────────┘
          │
          ├──► Stored in Session State
          │
          └──► Persisted to Browser localStorage
                    │
                    ▼
           Token injected in all
           subsequent API requests
```

**Session State Variables:**
- `token`: JWT authentication token
- `user`: User profile data (name, email, role)
- `student_id`: Student identifier
- `is_admin`: Admin role flag

### 2. Topic Selection System

The application offers five optimization topics for personalized learning:

| Internal Key            | Display Name (Spanish)       |
|-------------------------|------------------------------|
| `operations_research`   | Investigacion de Operaciones |
| `mathematical_modeling` | Modelado Matematico          |
| `linear_programming`    | Programacion Lineal          |
| `integer_programming`   | Programacion Entera          |
| `nonlinear_programming` | Programacion No Lineal       |

Topics are defined centrally in `utils/constants.py` for consistency.

### 3. Chat Interface

- Real-time conversation with topic-specialized AI agents
- Message history maintained in the session state
- Conversation tracking via `conversation_id`
- Agent type attribution is displayed for each response

### 4. Backend Health Check

The application performs periodic health checks:
```python
def check_backend_health():
    response = requests.get(f"{BACKEND_URL}/health")
    return response.status_code == 200
```

### 5. Role-Based Access Control

| Role  | Access                           |
|-------|----------------------------------|
| User  | Home, Chat, Assessment, Progress |
| Admin | All above + Admin Dashboard      |

Access checks are performed on each page load.

## API Communication

All API calls route through `utils/api_client.py`:

| Method     | Usage                                         |
|------------|-----------------------------------------------|
| `get()`    | Fetch data (progress, assessments, users)     |
| `post()`   | Create resources (chat messages, assessments) |
| `put()`    | Update resources (user status, roles)         |
| `delete()` | Remove resources                              |

Error handling includes automatic logout on 401 (token expired).

## Session State Management

Key session variables managed across pages:

| Variable          | Purpose                      |
|-------------------|------------------------------|
| `api_client`      | Singleton APIClient instance |
| `token`           | JWT authentication token     |
| `user`            | Current user profile         |
| `student_id`      | Student identifier           |
| `selected_topic`  | User's chosen learning topic |
| `chat_messages`   | Chat conversation history    |
| `conversation_id` | Active conversation tracker  |

## Changelog

| Version | Date       | Changes                                                                            |
|---------|------------|------------------------------------------------------------------------------------|
| 1.0.0   | 2026-01-05 | Initial documentation created                                                      |
| 1.1.0   | 2026-02-03 | Added some tools, exercise features, basic user restrictiveness to `@usach` domain |
| 1.1.1   | 2026-02-07 | New exercises were added                                                           |
| v1.2.1  | 2026-02-13 | New functionality for locked and unlocked exercises                                |
| v1.3.1  | 2026-02-16 | Added concept-level mastery tracking — when assessments are graded                 |
| v1.3.2  | 2026-02-17 | Added and fixed logout functionality                                               |
| v1.3.3  | 2026-02-17 | Fixed assessment behavior                                                          |