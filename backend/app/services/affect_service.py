import logging

from sqlalchemy.orm import Session

from ..database import ActivityEvent
from ..enums import AffectState, EventCategory

logger = logging.getLogger(__name__)

# --- Thresholds ---
_FRUSTRATION_TOPIC_SWITCHES = 3  # ≥ N TOPIC_CHANGE events in session
_BOREDOM_IDLE_SECONDS = 120.0  # total idle duration ≥ N seconds in session
_BOREDOM_IDLE_FREQUENCY = 3  # ≥ N IDLE_START events in session
_DISENGAGEMENT_WINDOW_SECONDS = 60.0  # session ended within N seconds after a failed assessment
_MIN_CONFIDENCE_TO_REPORT = 0.2  # below this → NEUTRAL


class AffectDetectionService:
    """
    Classifies the student's current affective state from session ActivityEvent records
    and the current message's confusion level.

    States: ENGAGED, FRUSTRATED, BORED, DISENGAGED, NEUTRAL
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def detect(
        self,
        student_id: int,
        session_id: str,
        confusion_analysis: dict,
    ) -> dict:
        """
        Classify the student's affective state for the current session.

        Args:
            student_id: Authenticated student ID.
            session_id: Frontend-generated session identifier.
            confusion_analysis: Output of detect_confusion_signals() for the current message.
                                 Expected keys: "detected", "level", "signals".
                                 Optionally "repeated_topic" with "count".

        Returns:
            {
                "state": AffectState value (str),
                "confidence": float (0.0–1.0),
                "signals": list[str],
            }
        """
        events = (
            self.db.query(ActivityEvent)
            .filter(
                ActivityEvent.student_id == student_id,
                ActivityEvent.session_id == session_id,
            )
            .order_by(ActivityEvent.timestamp)
            .all()
        )

        signals: list[str] = []
        scores: dict[AffectState, float] = {s: 0.0 for s in AffectState}

        # ── Frustration signals ────────────────────────────────────────────────
        topic_changes = sum(
            1 for e in events if e.event_category == EventCategory.TOPIC_CHANGE
        )
        if topic_changes >= _FRUSTRATION_TOPIC_SWITCHES:
            signals.append(f"rapid_topic_switching:{topic_changes}")
            scores[AffectState.FRUSTRATED] += 0.5

        confusion_level = confusion_analysis.get("level", "none")
        if confusion_level == "high":
            signals.append("high_confusion")
            scores[AffectState.FRUSTRATED] += 0.4
        elif confusion_level == "medium":
            signals.append("medium_confusion")
            scores[AffectState.FRUSTRATED] += 0.2

        repeated_count = confusion_analysis.get("repeated_topic", {}).get("count", 0)
        if repeated_count >= 3:
            signals.append("repeated_topic_escalation")
            scores[AffectState.FRUSTRATED] += 0.3

        # ── Boredom signals ────────────────────────────────────────────────────
        idle_start_events = [
            e for e in events if e.event_category == EventCategory.IDLE_START
        ]
        idle_duration = sum(
            e.duration_seconds or 0.0
            for e in events
            if e.event_category == EventCategory.IDLE_END and e.duration_seconds
        )
        if idle_duration >= _BOREDOM_IDLE_SECONDS:
            signals.append(f"long_idle_duration:{int(idle_duration)}s")
            scores[AffectState.BORED] += 0.5
        if len(idle_start_events) >= _BOREDOM_IDLE_FREQUENCY:
            signals.append(f"frequent_idle_events:{len(idle_start_events)}")
            scores[AffectState.BORED] += 0.3

        # ── Disengagement signals ──────────────────────────────────────────────
        session_end_events = [
            e for e in events if e.event_category == EventCategory.SESSION_END
        ]
        assessment_failures = [
            e
            for e in events
            if e.event_category == EventCategory.ASSESSMENT_SUBMIT
            and (e.extra_data or {}).get("passed") is False
        ]
        if session_end_events and assessment_failures:
            last_failure = max(assessment_failures, key=lambda e: e.timestamp)
            last_end = max(session_end_events, key=lambda e: e.timestamp)
            delta = (last_end.timestamp - last_failure.timestamp).total_seconds()
            if 0.0 <= delta <= _DISENGAGEMENT_WINDOW_SECONDS:
                signals.append("quit_after_failure")
                scores[AffectState.DISENGAGED] += 0.6

        # ── Engagement signals ─────────────────────────────────────────────────
        chat_messages = sum(
            1 for e in events if e.event_category == EventCategory.CHAT_MESSAGE
        )
        if (
            chat_messages >= 5
            and not idle_start_events
            and confusion_level in ("none", "low")
        ):
            signals.append("active_low_confusion_session")
            scores[AffectState.ENGAGED] += 0.7

        # ── Determine dominant state ───────────────────────────────────────────
        best_state = max(scores, key=lambda s: scores[s])
        best_score = scores[best_state]

        if best_score < _MIN_CONFIDENCE_TO_REPORT:
            best_state = AffectState.NEUTRAL
            best_score = 1.0

        logger.info(
            "Affect detection: state=%s, confidence=%.2f, signals=%s",
            best_state,
            min(best_score, 1.0),
            signals,
        )

        return {
            "state": best_state,
            "confidence": min(best_score, 1.0),
            "signals": signals,
        }


def get_affect_service(db: Session) -> AffectDetectionService:
    return AffectDetectionService(db)
