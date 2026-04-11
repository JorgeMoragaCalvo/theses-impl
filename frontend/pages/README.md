# Pages Module

## Overview

This module contains the Streamlit multipage application pages. Each page is a separate Python file that Streamlit automatically discovers and adds to the navigation sidebar.

Pages are numbered (e.g., `1_chat.py`) to control their display order in the sidebar navigation.

## File Structure

```diagram
pages/
├── __init__.py          # Python package marker
├── 1_chat.py            # Chat interface page
├── 2_assessment.py      # Assessment and practice page
├── 3_progress.py        # Progress tracking page
└── 4_admin.py           # Admin dashboard page
```

## Documentation

### Streamlit Multi-Page Architecture

Streamlit automatically detects Python files in the `pages/` directory and creates navigation entries. The naming convention:
- Files prefixed with numbers appear in sorted order
- Underscores are replaced with spaces in the sidebar
- Example: `1_chat.py` appears as "Chat" in navigation

---

## Page Details

### 1. Chat Page (`1_chat.py`)

**Purpose:** Dedicated chat interface for conversations with AI tutors

**Key Features:**
- Topic-specific chat selection
- Real-time AI response display
- Agent type attribution (shows which AI agent responded)
- Conversation history within a session
- Clear conversation functionality
- Learning tips sidebar

**Session State:**

| Variable               | Type | Purpose                        |
|------------------------|------|--------------------------------|
| `chat_messages`        | list | Conversation message history   |
| `chat_conversation_id` | str  | Active conversation identifier |

**API Endpoints Used:**

| Endpoint | Method | Purpose                              |
|----------|--------|--------------------------------------|
| `/chat`  | POST   | Send message and receive AI response |

---

### 2. Assessment Page (`2_assessment.py`)

**Purpose:** Comprehensive practice and assessment system for student evaluation

**Size:** Largest page (~593 lines) – Most complex functionality

**Tabs:**
1. **Progress Dashboard** – Overview of learning metrics
2. **Assessment History** – Past assessments and grades
3. **New Assessment** – Generate and complete new assessments

**Key Features:**

#### Tab 1: Progress Dashboard
- Student progress metrics display
- Knowledge level indicators per topic (Beginner/Intermediate/Advanced)
- Topic-covered badges
- Recent activity timeline
- Assessment status tracking

#### Tab 2: Assessment History
- Filter assessments by topic
- Sort by creation date
- Status indicators:
  - ✅ Auto-graded / Admin graded / Reviewed
  - ⏳ Pending (not submitted)
  - ⌛ Submitted (awaiting grade)
- Score and feedback display
- Late submission support

#### Tab 3: New Assessment
- **Mode A:** Standard LLM-generated problems
  - Select topic and difficulty
  - AI generates contextual problems
- **Mode B:** Practice from existing exercises
  - Browse exercise library
  - Original or AI-generated similar problems

**Session State:**

| Variable               | Type | Purpose                           |
|------------------------|------|-----------------------------------|
| `current_assessment`   | dict | Active assessment being worked on |
| `show_assessment_form` | bool | UI visibility control             |

**API Endpoints Used:**

| Endpoint                   | Method | Purpose                            |
|----------------------------|--------|------------------------------------|
| `/students/{id}/progress`  | GET    | Fetch student progress             |
| `/assessments`             | GET    | List student assessments           |
| `/assessments/{id}`        | GET    | Get single assessment              |
| `/assessments/generate`    | POST   | Generate new assessment            |
| `/assessments/{id}/submit` | POST   | Submit assessment answer           |
| `/exercises`               | GET    | List available exercises           |
| `/exercises/{id}/generate` | POST   | Generate exercise-based assessment |

**Helper Functions:**
```python
fetch_student_progress(student_id)      # Get overall progress metrics
fetch_assessments(student_id, topic)    # Get assessment history
fetch_single_assessment(assessment_id)  # Get single assessment details
generate_assessment(topic, difficulty)  # Generate new AI assessment
submit_assessment(assessment_id, answer)# Submit an answer for grading
fetch_exercises()                       # Get available exercises
generate_exercise_assessment(id, mode)  # Generate exercise-based assessment
```

---

### 3. Progress Page (`3_progress.py`)

**Purpose:** Student learning analytics and progress visualization

**Key Features:**
- Student profile display (name, email, member since)
- Knowledge level indicators with color coding
- Conversation history retrieval
- Learning statistics aggregation
- Detailed conversation viewer

**Knowledge Level Colors:**

| Level        | Color  | Badge |
|--------------|--------|-------|
| Beginner     | Red    | `🔴`  |
| Intermediate | Yellow | `🟡`  |
| Advanced     | Green  | `🟢`  |

**Statistics Displayed:**
- Total messages sent
- Practice problems completed
- Average assessment score
- Total conversations
- Member tenure

**Session State:**
Uses shared session state from the main app (no page-specific state).

**API Endpoints Used:**

| Endpoint                       | Method | Purpose                  |
|--------------------------------|--------|--------------------------|
| `/students/{id}`               | GET    | Fetch student profile    |
| `/students/{id}/progress`      | GET    | Fetch progress metrics   |
| `/students/{id}/conversations` | GET    | List conversations       |
| `/conversations/{id}`          | GET    | Get conversation details |

---

### 4. Admin Page (`4_admin.py`)

**Purpose:** System administration and user management (admin-only access)

**Access Control:**
```python
if not api_client.is_authenticated():
    st.error("Please log in")
    return

if not api_client.is_admin():
    st.error("Admin access required")
    return
```

**Tabs:**
1. **User Management** – Manage all system users
2. **System Statistics** – View system-wide metrics
3. **Settings** – View system configuration

**Key Features:**

#### Tab 1: User Management
- List all users with statistics
- User metrics: total, active, inactive, admin count
- User data table showing:
  - User ID, Name, Email, Role
  - Status (active/inactive)
  - Conversation and assessment count
  - Average score
  - Creation date and last login
- Individual user actions:
  - Activate/Deactivate accounts
  - Change roles (user ↔ admin)

#### Tab 2: System Statistics
- Total users and active users
- Total conversations and assessments
- Average assessment score system-wide
- Usage analytics placeholders

#### Tab 3: Settings
- Display the current configuration (read-only):
  - LLM provider and model
  - Temperature and max tokens
  - System version
  - Debug mode status
  - Session timeout

**API Endpoints Used:**

| Endpoint                   | Method | Purpose                  |
|----------------------------|--------|--------------------------|
| `/admin/users`             | GET    | List all users           |
| `/admin/users/{id}/status` | PUT    | Activate/deactivate user |
| `/admin/users/{id}/role`   | PUT    | Change user role         |
| `/admin/stats`             | GET    | System statistics        |
| `/admin/settings`          | GET    | System configuration     |

---

## Business Logic

### Navigation Flow

```diagram
┌─────────────┐
│   app.py    │ (Home - Login/Register)
│   (Home)    │
└──────┬──────┘
       │ Authenticated
       ▼
┌─────────────────────────────────────────────┐
│              Streamlit Sidebar              │
├──────────┬──────────┬──────────┬────────────┤
│  Chat    │Assessment│ Progress │   Admin    │
│  (1)     │   (2)    │   (3)    │   (4)*     │
└──────────┴──────────┴──────────┴────────────┘
                                  * Admin only
```

### Page Lifecycle

Each page follows this pattern:
1. Check authentication status
2. Check role permissions (if applicable)
3. Initialize page-specific session state
4. Fetch required data from API
5. Render UI components
6. Handle user interactions
7. Update session state on changes

### Error Handling

All pages implement consistent error handling:
```python
success, data = api_client.get("/endpoint")
if success:
    # Process data
else:
    st.error(data.get("error", "An error occurred"))
```

## Changelog

| Version | Date       | Changes                                                                            |
|---------|------------|------------------------------------------------------------------------------------|
| v1.0.0  | 2026-01-05 | Initial documentation created                                                      |
| v1.1.0  | 2026-02-03 | Added some tools, exercise features, basic user restrictiveness to `@usach` domain |
| v1.1.1  | 2026-02-07 | New exercises were added                                                           |
| v1.2.1  | 2026-02-13 | New functionality for locked and unlocked exercises                                |
| v1.3.1  | 2026-02-16 | Added concept-level mastery tracking — when assessments are graded                 |
| v1.3.2  | 2026-02-17 | Added and fixed logout functionality                                               |
| v1.3.3  | 2026-02-17 | Fixed assessment behavior                                                          |
| v1.4.3  | 2026-02-18 | Record student's activity                                                          |
| v1.5.3  | 2026-02-19 | Spaced Repetition System                                                           |
| v1.5.4  | 2026-02-25 | Fixed some bugs                                                                    |
| v1.6.4  | 2026-02-27 | Added testing implementation                                                       |
| v1.6.5  | 2026-04-03 | Security, routing and main.py improvements                                         |
| v1.6.6  | 2026-04-06 | Coverage tests                                                                     |
| v1.6.7  | 2026-04-11 | Code review and exercises                                                          |