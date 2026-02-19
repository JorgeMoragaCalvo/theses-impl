# Utils Module

## Overview

This module contains shared utility functions and classes used across all frontend pages. It provides centralized API communication and constant definitions.

## File Structure

```diagram
utils/
├── __init__.py      # Python package marker
├── api_client.py    # HTTP client with JWT authentication
└── constants.py     # Shared constants and topic definitions
```

---

## Documentation

### api_client.py

**Purpose:** Centralized HTTP client for all API calls with JWT token management

**Size:** ~324 lines

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
- Primary: Streamlit session state (`st.session_state.token`)
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
    Returns singleton APIClient instance from session state.
    Creates new instance if not exists.
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
    "operations_research": "Investigacion de Operaciones",
    "mathematical_modeling": "Modelado Matematico",
    "linear_programming": "Programacion Lineal",
    "integer_programming": "Programacion Entera",
    "nonlinear_programming": "Programacion No Lineal"
}
```

**TOPIC_OPTIONS**
Reverse mapping from display names to internal keys:
```python
TOPIC_OPTIONS = {
    "Investigacion de Operaciones": "operations_research",
    "Modelado Matematico": "mathematical_modeling",
    # ... etc
}
```

**TOPICS_LIST**
Ordered list of topic display names for dropdowns:
```python
TOPICS_LIST = [
    "Programacion Lineal",
    "Programacion Entera",
    "Programacion No Lineal",
    "Modelado Matematico",
    "Investigacion de Operaciones"
]
```

**TOPIC_DESCRIPTIONS**
Detailed descriptions for each topic (used in UI):
```python
TOPIC_DESCRIPTIONS = {
    "linear_programming": "Learn to optimize...",
    # ... etc
}
```

**DEFAULT_TOPIC**
Default selected topic:
```python
DEFAULT_TOPIC = "Programacion Lineal"
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
# Returns: "Programacion Lineal"
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
st.session_state.token = "jwt_token_here"
st.session_state.user = {"name": "...", "email": "...", "role": "..."}
st.session_state.student_id = "..."
st.session_state.is_admin = True/False

# Accessed via APIClient methods
api_client.is_authenticated()  # Checks st.session_state.token
api_client.is_admin()          # Checks st.session_state.is_admin
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