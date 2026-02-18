import uuid
from datetime import datetime, timezone
from typing import Any

import streamlit as st

"""
Activity tracking utility for frontend analytics.
Batches events in session state and sends them to the backend.
All analytics data is visible only to admin users.
"""

# Page name constants
PAGE_HOME = "home"
PAGE_CHAT = "chat"
PAGE_ASSESSMENT = "assessment"
PAGE_PROGRESS = "progress"
PAGE_ADMIN = "admin"


def _get_session_id() -> str:
    """Get or create a unique session ID for this browser session."""
    if "_analytics_session_id" not in st.session_state:
        st.session_state._analytics_session_id = str(uuid.uuid4())
    return st.session_state._analytics_session_id


def _get_event_buffer() -> list[dict]:
    """Get the event buffer from the session state."""
    if "_analytics_event_buffer" not in st.session_state:
        st.session_state._analytics_event_buffer = []
    return st.session_state._analytics_event_buffer


def _add_event(
    event_category: str,
    event_action: str,
    page_name: str | None = None,
    topic: str | None = None,
    duration_seconds: float | None = None,
    extra_data: dict[str, Any] | None = None,
):
    """Add an event to the buffer. Auto-flushes at 10 events."""
    if "access_token" not in st.session_state:
        return

    buffer = _get_event_buffer()
    buffer.append({
        "session_id": _get_session_id(),
        "event_category": event_category,
        "event_action": event_action,
        "page_name": page_name,
        "topic": topic,
        "duration_seconds": duration_seconds,
        "extra_data": extra_data or {},
    })

    if len(buffer) >= 10:
        flush_events()


def track_page_visit(page_name: str, topic: str | None = None):
    """Track a page visit. Only records when the page actually changes (not on reruns)."""
    prev_page = st.session_state.get("_analytics_current_page")

    if prev_page == page_name:
        # Same page rerun — don't record again, but flush if the buffer is large
        if len(_get_event_buffer()) >= 10:
            flush_events()
        return

    # Page changed — record exit from the previous page with duration
    now = datetime.now(timezone.utc)
    prev_timestamp = st.session_state.get("_analytics_page_enter_time")

    if prev_page and prev_timestamp:
        duration = (now - prev_timestamp).total_seconds()
        if 0 < duration < 3600:  # Cap at 1 hour to filter stale sessions
            _add_event(
                "page_exit", "page_leave",
                page_name=prev_page,
                duration_seconds=round(duration, 1),
            )

    # Record the new page visit
    st.session_state._analytics_current_page = page_name
    st.session_state._analytics_page_enter_time = now
    _add_event("page_visit", "page_view", page_name=page_name, topic=topic)


def track_interaction(
    action: str,
    page_name: str,
    topic: str | None = None,
    extra_data: dict[str, Any] | None = None,
):
    """Track a widget interaction (Layer 2)."""
    _add_event(
        "widget_interaction", action,
        page_name=page_name, topic=topic, extra_data=extra_data,
    )


def track_chat_message(
    page_name: str,
    topic: str,
    conversation_id: int | None = None,
):
    """Track a chat message sent (Layer 2)."""
    _add_event(
        "chat_message", "chat_send",
        page_name=page_name, topic=topic,
        extra_data={"conversation_id": conversation_id},
    )


def track_assessment_generate(
    topic: str,
    difficulty: str | None = None,
    exercise_id: str | None = None,
):
    """Track assessment generation (Layer 2)."""
    _add_event(
        "assessment_generate", "assessment_generate",
        page_name=PAGE_ASSESSMENT, topic=topic,
        extra_data={"difficulty": difficulty, "exercise_id": exercise_id},
    )


def track_assessment_submit(assessment_id: int, topic: str):
    """Track assessment submission (Layer 2)."""
    _add_event(
        "assessment_submit", "assessment_submit",
        page_name=PAGE_ASSESSMENT, topic=topic,
        extra_data={"assessment_id": assessment_id},
    )


def track_topic_change(new_topic: str, page_name: str):
    """Track topic selection change (Layer 2)."""
    _add_event(
        "topic_change", "topic_select",
        page_name=page_name, topic=new_topic,
    )


def flush_events():
    """Send buffered events to the backend. Silently fails to never break UX."""
    buffer = _get_event_buffer()
    if not buffer:
        return

    if "access_token" not in st.session_state:
        return

    try:
        from utils.api_client import get_api_client
        api_client = get_api_client(st.session_state.get("_backend_url", "http://localhost:8000"))
        api_client.post("/analytics/events", json_data={"events": buffer})
    except Exception:
        pass  # Analytics should never break the user experience

    # Clear buffer regardless of success
    st.session_state._analytics_event_buffer = []
