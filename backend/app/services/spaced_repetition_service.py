import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..database import (
    ReviewSession,
    StudentCompetency,
    Topic,
)
from .competency_service import CompetencyService

"""
Spaced Repetition Service - SM-2 algorithm implementation.
Schedules concept reviews at increasing intervals based on recall quality.
"""

logger = logging.getLogger(__name__)


def _sanitize_log_value(value: str) -> str:
    """
    Sanitize a value for safe logging by stripping newline characters.

    This helps prevent log injection when values may come from user input.
    """
    if value is None:
        return ""
    # Remove carriage returns and newlines that could inject extra log entries
    return value.replace("\r", "").replace("\n", "")


# SM-2 initial intervals in days (used for first successful reviews)
INITIAL_INTERVALS = [1, 3, 7, 14, 30, 60]

# Minimum ease factor (decay_factor) per SM-2 spec
MIN_EASE_FACTOR = 1.3

# Default ease factor for new competencies
DEFAULT_EASE_FACTOR = 2.5

# Performance quality threshold: below this the concept needs relearning
QUALITY_PASSING_THRESHOLD = 3


class SpacedRepetitionService:
    """SM-2 based spaced repetition for concept review scheduling."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Core SM-2 calculation
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_next_review(
        competency: StudentCompetency,
        performance_quality: int,
    ) -> tuple[datetime, float]:
        """
        SM-2 algorithm: compute the next review date and updated ease factor.

        Args:
            competency: The student's competency record for the concept.
            performance_quality: Quality of recall, 0-5 scale
                0 - Complete blackout
                1 - Incorrect; correct answer remembered on seeing it
                2 - Incorrect; correct answer seemed easy to recall
                3 - Correct with serious difficulty
                4 - Correct after hesitation
                5 - Perfect response

        Returns:
            Tuple of (next_review_datetime, new_ease_factor)
        """
        now = datetime.now(timezone.utc)
        ease_factor = competency.decay_factor or DEFAULT_EASE_FACTOR

        if performance_quality < QUALITY_PASSING_THRESHOLD:
            # Failed recall — reset to a short interval, decrease an ease factor
            interval_days = INITIAL_INTERVALS[0]
            ease_factor = max(MIN_EASE_FACTOR, ease_factor - 0.2)
        else:
            # Successful recall — compute a new ease factor
            ease_bonus = 0.1 - (5 - performance_quality) * (0.08 + (5 - performance_quality) * 0.02)
            ease_factor = max(MIN_EASE_FACTOR, ease_factor + ease_bonus)

            # Determine the interval
            review_count = _count_successful_reviews(competency)
            if review_count < len(INITIAL_INTERVALS):
                interval_days = INITIAL_INTERVALS[review_count]
            else:
                # After the initial ramp-up, multiply the last interval by ease factor
                prev_interval = _get_previous_interval_days(competency)
                interval_days = int(prev_interval * ease_factor)

        next_review = now + timedelta(days=interval_days)
        return next_review, ease_factor

    # ------------------------------------------------------------------
    # Due reviews
    # ------------------------------------------------------------------

    def get_due_reviews(
        self,
        student_id: int,
        topic: str | None = None,
        limit: int = 5,
    ) -> list[StudentCompetency]:
        """
        Return competencies that are due for review (next_review_at <= now).

        Args:
            student_id: Student ID
            topic: Optional topic filter
            limit: Max number of results

        Returns:
            List of StudentCompetency records due for review, ordered by
            next_review_at ascending (most overdue first).
        """
        now = datetime.now(timezone.utc)

        query = self.db.query(StudentCompetency).filter(
            StudentCompetency.student_id == student_id,
            StudentCompetency.next_review_at <= now,
            StudentCompetency.attempts_count > 0,
        )

        if topic:
            try:
                topic_enum = Topic(topic)
                query = query.filter(StudentCompetency.topic == topic_enum)
            except ValueError:
                safe_topic = _sanitize_log_value(str(topic))
                logger.warning(f"Unknown topic for due reviews: {safe_topic}")
                return []

        return (
            query
            .order_by(StudentCompetency.next_review_at.asc())
            .limit(limit)
            .all()
        )

    # ------------------------------------------------------------------
    # Start a review session
    # ------------------------------------------------------------------

    def create_review_session(
        self,
        student_id: int,
        concept_id: str,
    ) -> ReviewSession:
        """
        Create a new ReviewSession for a concept, marking it as scheduled now.

        Args:
            student_id: Student ID
            concept_id: Concept to review

        Returns:
            The created ReviewSession
        """
        now = datetime.now(timezone.utc)

        session = ReviewSession(
            student_id=student_id,
            concept_id=concept_id,
            scheduled_at=now,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        safe_student_id = _sanitize_log_value(str(student_id))
        safe_concept = _sanitize_log_value(str(concept_id))

        logger.info(
            f"Created review session {session.id} for student={safe_student_id}, "
            f"concept={safe_concept}"
        )
        return session

    # ------------------------------------------------------------------
    # Complete a review
    # ------------------------------------------------------------------

    def complete_review(
        self,
        review_session_id: int,
        performance_quality: int,
        response_time_seconds: float | None = None,
    ) -> ReviewSession:
        """
        Record the result of a review session and schedule the next review.

        Args:
            review_session_id: ReviewSession ID
            performance_quality: SM-2 quality rating 0-5
            response_time_seconds: Optional time the student took

        Returns:
            The updated ReviewSession

        Raises:
            ValueError: If a review session is not found or already completed
        """
        session = self.db.query(ReviewSession).filter(
            ReviewSession.id == review_session_id,
        ).first()

        if session is None:
            raise ValueError(f"Review session {review_session_id} not found")
        if session.completed_at is not None:
            raise ValueError(f"Review session {review_session_id} already completed")

        now = datetime.now(timezone.utc)

        # Look up the competency
        competency = self.db.query(StudentCompetency).filter(
            StudentCompetency.student_id == session.student_id,
            StudentCompetency.concept_id == session.concept_id,
        ).first()

        if competency is None:
            raise ValueError(
                f"No competency record for student={session.student_id}, "
                f"concept={session.concept_id}"
            )

        # Run SM-2 calculation
        next_review_at, new_ease_factor = self.calculate_next_review(
            competency, performance_quality
        )

        # Update competency scheduling fields
        competency.decay_factor = new_ease_factor
        competency.next_review_at = next_review_at

        # Optionally update mastery via CompetencyService
        is_correct = performance_quality >= QUALITY_PASSING_THRESHOLD
        normalized_score = performance_quality / 5.0
        competency_svc = CompetencyService(self.db)
        competency_svc.update_competency(
            student_id=session.student_id,
            concept_id=session.concept_id,
            is_correct=is_correct,
            performance_score=normalized_score,
        )
        # Re-read competency after update_competency committed
        competency = self.db.query(StudentCompetency).filter(
            StudentCompetency.student_id == session.student_id,
            StudentCompetency.concept_id == session.concept_id,
        ).first()
        # Reapply scheduling fields (update_competency doesn't touch them)
        competency.decay_factor = new_ease_factor
        competency.next_review_at = next_review_at

        # Update the review session record
        session.performance_quality = performance_quality
        session.response_time_seconds = response_time_seconds
        session.completed_at = now
        session.next_review_scheduled = next_review_at

        self.db.commit()
        self.db.refresh(session)

        logger.info(
            f"Completed review session {session.id}: quality={performance_quality}, "
            f"next_review={next_review_at.isoformat()}, ease={new_ease_factor:.2f}"
        )
        return session

    # ------------------------------------------------------------------
    # Schedule initial review after assessment grading
    # ------------------------------------------------------------------

    def schedule_initial_review(
        self,
        student_id: int,
        concept_id: str,
    ) -> None:
        """
        Schedule the first review for a concept after it has been studied.
        Called after grading when a concept is first encountered.
        Only schedules if next_review_at is not already set.
        """
        competency = self.db.query(StudentCompetency).filter(
            StudentCompetency.student_id == student_id,
            StudentCompetency.concept_id == concept_id,
        ).first()

        if competency is None or competency.next_review_at is not None:
            return

        # Schedule first review in 1 day
        competency.next_review_at = datetime.now(timezone.utc) + timedelta(days=1)
        self.db.commit()

        logger.info(
            f"Scheduled initial review for student={student_id}, concept={concept_id} "
            f"at {competency.next_review_at.isoformat()}"
        )


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _count_successful_reviews(competency: StudentCompetency) -> int:
    """
    Approximate the number of consecutive successful reviews.
    Uses correct_count as a proxy (exact tracking would need full history).
    """
    return competency.correct_count or 0


def _get_previous_interval_days(competency: StudentCompetency) -> int:
    """
    Estimate the previous interval in days from stored timestamps.
    Falls back to the last entry in INITIAL_INTERVALS if unavailable.
    """
    if competency.next_review_at and competency.last_correct_at:
        # The previous interval is roughly (next_review_at - last_correct_at)
        delta = competency.next_review_at - competency.last_correct_at
        days = max(1, delta.days)
        return days
    return INITIAL_INTERVALS[-1]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_spaced_repetition_service(db: Session) -> SpacedRepetitionService:
    return SpacedRepetitionService(db)
