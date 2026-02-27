# Utils Module

## Overview

This module contains shared utility functions and classes used across all frontend pages. It provides centralized API communication, constant definitions, and analytics tracking.

## File Structure

```diagram
utils/
├── __init__.py          # Python package marker
├── activity_tracker.py  # Event-based analytics tracking (Python/server-side)
├── api_client.py        # HTTP client with JWT authentication
├── constants.py         # Shared constants and topic definitions
└── idle_detector.py     # JavaScript-based idle/focus detection (client-side)
```

---

## Documentation

### api_client.py

**Purpose:** Centralized HTTP client for all API calls with JWT token management

**Size:** ~330 lines

#### APIClient Class

The main class handling all HTTP communication with the backend.

**Initialization:**
```python
client = APIClient(base_url="http://localhost:8000")
```

**Configuration:**
- Default timeout: 30 seconds
- Automatic Bearer token injection
- Session state integration with Streamlit

---

#### HTTP Methods

| Method     | Signature                                   | Returns            |
|------------|---------------------------------------------|--------------------|
| `get()`    | `get(endpoint, params=None)`                | `tuple[bool, Any]` |
| `post()`   | `post(endpoint, data=None, json_data=None)` | `tuple[bool, Any]` |
| `put()`    | `put(endpoint, data=None, json_data=None)`  | `tuple[bool, Any]` |
| `delete()` | `delete(endpoint)`                          | `tuple[bool, Any]` |

**Return Pattern:**
All methods return a tuple `(success: bool, data: dict)`:
- Success: `(True, response_data)`
- Failure: `(False, {"error": "error message"})`

**Usage Example:**
```python
api_client = get_api_client("http://localhost:8000")

# GET request
success, data = api_client.get("/students/123/progress")
if success:
    progress = data
else:
    print(f"Error: {data['error']}")

# POST request
success, data = api_client.post("/chat", json_data={
    "message": "Hello",
    "topic": "linear_programming"
})
```

---

#### Authentication Methods

| Method                            | Purpose                            |
|-----------------------------------|------------------------------------|
| `register(name, email, password)` | Create new user account            |
| `login(email, password)`          | Authenticate and receive JWT token |
| `logout()`                        | Clear token and session data       |
| `get_current_user()`              | Fetch current user profile         |
| `is_authenticated()`              | Check if user has valid token      |
| `is_admin()`                      | Check if user has admin role       |

**Login Flow:**
```python
success, data = api_client.login("user@example.com", "password")
if success:
    # Token automatically stored
    # User data available in session state
    print(f"Welcome, {data['user']['name']}")
```

---

#### Token Management

**Internal Methods:**

| Method                        | Purpose                                   |
|-------------------------------|-------------------------------------------|
| `_get_headers()`              | Build request headers with Bearer token   |
| `_handle_response()`          | Process HTTP response, detect auth errors |
| `_store_auth_data()`          | Save token and user to session state      |
| `_store_token_in_browser()`   | Persist token to browser localStorage     |
| `_clear_token_from_browser()` | Remove token from localStorage            |
| `load_token_from_browser()`   | Load token from localStorage              |

**Token Storage:**
- Primary: Streamlit session state (`st.session_state.access_token`)
- Secondary: Browser localStorage (via JavaScript injection)

---

#### Error Handling

| HTTP Status | Behavior                                 |
|-------------|------------------------------------------|
| 200-299     | Success, return response data            |
| 401         | Unauthorized - auto logout, return error |
| 403         | Forbidden - return permission error      |
| 4xx         | Client error - return error message      |
| 5xx         | Server error - return error message      |

---

#### Helper Function

```python
def get_api_client(base_url: str) -> APIClient:
    """
    Returns a singleton APIClient instance from a session state.
    Creates a new instance if not exists.
    """
```

**Usage:**
```python
from utils.api_client import get_api_client

BACKEND_URL = "http://localhost:8000"
api_client = get_api_client(BACKEND_URL)
```

---

### constants.py

**Purpose:** Define topic options and descriptions used across all pages

**Size:** ~65 lines

#### Constants Defined

**TOPIC_DISPLAY_NAMES**
Maps internal topic keys to Spanish display names:
```python
TOPIC_DISPLAY_NAMES = {
    "operations_research": "Investigación de Operaciones",
    "mathematical_modeling": "Modelado Matemático",
    "linear_programming": "Programación Lineal",
    "integer_programming": "Programación Entera",
    "nonlinear_programming": "Programación No Lineal"
}
```

**TOPIC_OPTIONS**
Reverse mapping from display names to internal keys:
```python
TOPIC_OPTIONS = {
    "Investigación de Operaciones": "operations_research",
    "Modelado Matemático": "mathematical_modeling",
    # ... etc
}
```

**TOPICS_LIST**
Ordered list of topic display names for dropdowns:
```python
TOPICS_LIST = [
    "Investigación de Operaciones",
    "Modelado Matemático",
    "Programación Lineal",
    "Programación Entera",
    "Programación No Lineal"
]
```

**TOPIC_DESCRIPTIONS**
Subtopic lists for each topic (used in the welcome screen UI):
```python
TOPIC_DESCRIPTIONS = {
    "Investigación de Operaciones": [
        "Introducción a la optimización",
        "Fundamentos de formulación de problemas",
        "Marcos de toma de decisiones"
    ],
    "Programación Lineal": [
        "Formulación y solución de PL",
        "Método Simplex",
        "Teoría de dualidad"
    ],
    # ... etc
}
```

**DEFAULT_TOPIC**
Default selected topic:
```python
DEFAULT_TOPIC = "Programación Lineal"
```

---

#### Usage Examples

```python
from utils.constants import (
    TOPIC_OPTIONS,
    TOPIC_DISPLAY_NAMES,
    TOPICS_LIST,
    DEFAULT_TOPIC
)

# In a Streamlit dropdown
selected_display = st.selectbox("Select Topic", TOPICS_LIST)
internal_key = TOPIC_OPTIONS[selected_display]

# Converting internal key to display
display_name = TOPIC_DISPLAY_NAMES["linear_programming"]
# Returns: "Programación Lineal"
```

---

### activity_tracker.py

**Purpose:** Server-side (Python) event-based analytics tracking that batches events in Streamlit session state and sends them to the backend

**Size:** ~165 lines

#### Page Constants

```python
PAGE_HOME = "home"
PAGE_CHAT = "chat"
PAGE_ASSESSMENT = "assessment"
PAGE_PROGRESS = "progress"
PAGE_ADMIN = "admin"
```

#### Tracking Functions

| Function                      | Purpose                                                     |
|-------------------------------|-------------------------------------------------------------|
| `track_page_visit()`          | Track page visits with automatic duration on page exit      |
| `track_interaction()`         | Track widget interactions (clicks, selections)              |
| `track_chat_message()`        | Track chat messages sent with conversation ID               |
| `track_assessment_generate()` | Track assessment generation with topic and difficulty       |
| `track_assessment_submit()`   | Track assessment submissions with assessment ID             |
| `track_topic_change()`        | Track topic selection changes                               |
| `flush_events()`              | Send buffered events to the backend via `/analytics/events` |

#### Internal Functions

| Function               | Purpose                                          |
|------------------------|--------------------------------------------------|
| `_get_session_id()`    | Get or create a unique UUID session ID           |
| `_get_event_buffer()`  | Get the event buffer list from session state     |
| `_add_event()`         | Add an event to the buffer; auto-flushes at 10   |

#### Event Buffering

Events are accumulated in `st.session_state._analytics_event_buffer` and automatically flushed when the buffer reaches 10 events. The `flush_events()` function can also be called manually. All flushes silently fail to never break the user experience.

#### Usage Example

```python
from utils.activity_tracker import track_page_visit, track_chat_message, flush_events

# Track a page visit (automatically tracks duration on page exit)
track_page_visit("chat", topic="linear_programming")

# Track a chat message
track_chat_message("chat", topic="linear_programming", conversation_id=42)

# Manually flush buffered events
flush_events()
```

---

### idle_detector.py

**Purpose:** Client-side (JavaScript) idle detection and window focus/blur tracking injected into the browser via Streamlit components

**Size:** ~153 lines

#### Function

```python
def inject_idle_detector(
    backend_url: str = "http://localhost:8000",
    idle_timeout_seconds: int = 300,
)
```

#### Behavior

The injected JavaScript script:
- Tracks window **focus/blur** events (`session_start`/`session_end`)
- Detects **idle** after `idle_timeout_seconds` (default 300 s) of no mouse/keyboard/scroll activity
- Posts events directly to the backend via `fetch()` using the JWT token from `localStorage`
- Batches events in `localStorage` and flushes every 30 seconds
- Prevents multiple injections with a `window._idleDetectorInitialized` guard

#### Events Tracked

| Event Category   | Event Action    | Trigger                            |
|------------------|-----------------|------------------------------------|
| `session_start`  | `page_load`     | Initial page load with focus       |
| `session_start`  | `window_focus`  | Window regains focus               |
| `session_end`    | `window_blur`   | Window loses focus                 |
| `idle_start`     | `user_idle`     | No activity for idle timeout       |
| `idle_end`       | `user_active`   | Activity detected after idle state |

#### Usage Example

```python
from utils.idle_detector import inject_idle_detector

# Inject once per page (typically in the main app)
inject_idle_detector(backend_url="http://localhost:8000", idle_timeout_seconds=300)
```

---

## Business Logic

### API Communication Pattern

All pages follow this pattern for API calls:

```diagram
Page Component
      │
      ▼
┌─────────────────┐
│ get_api_client()│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   APIClient     │
│  .get/.post/... │
└────────┬────────┘
         │
         ├── Add Authorization header
         ├── Send HTTP request
         ├── Handle response
         │
         ▼
┌─────────────────┐
│ (success, data) │
└────────┬────────┘
         │
         ▼
   Page handles
   success/error
```

### Session State Integration

The APIClient integrates with Streamlit's session state:

```python
# Stored automatically on login
st.session_state.access_token = "jwt_token_here"
st.session_state.user = {"name": "...", "email": "...", "role": "..."}
st.session_state.student_id = "..."
st.session_state.student_name = "..."
st.session_state.student_email = "..."
st.session_state.user_role = "admin" | "student"

# Accessed via APIClient methods
api_client.is_authenticated()  # Checks st.session_state.access_token
api_client.is_admin()          # Checks st.session_state.user_role == "admin"
```

### Analytics Architecture

The analytics system operates in two layers:

```diagram
┌──────────────────────────────────────────────────┐
│               Frontend Analytics                 │
├──────────────────────┬───────────────────────────┤
│  activity_tracker.py │     idle_detector.py      │
│  (Python / server)   │     (JavaScript / client) │
├──────────────────────┼───────────────────────────┤
│  Page visits         │  Window focus/blur        │
│  Widget interactions │  Idle detection           │
│  Chat messages       │  User activity monitoring │
│  Assessment actions  │                           │
│  Topic changes       │                           │
├──────────────────────┼───────────────────────────┤
│  Buffers in session  │  Buffers in localStorage  │
│  state (10 events)   │  Flushes every 30 seconds │
├──────────────────────┴───────────────────────────┤
│          POST /analytics/events                  │
│          (backend API)                           │
└──────────────────────────────────────────────────┘
```

### Topic System Consistency

Constants ensure frontend-backend consistency:

1. **Frontend dropdown** uses `TOPICS_LIST` for display
2. **User selection** converted via `TOPIC_OPTIONS`
3. **API calls** use internal keys (e.g., `"linear_programming"`)
4. **Response display** uses `TOPIC_DISPLAY_NAMES` for UI

---

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
| v1.4.3  | 2026-02-18 | Record student's activity                                                          |
| v1.5.3  | 2026-02-19 | Spaced Repetition System                                                           |
| v1.5.4  | 2026-02-25 | Fixed some bugs                                                                    |
| v1.6.4  | 2026-02-27 | Added testing implementation                                                       |