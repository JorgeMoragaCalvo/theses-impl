import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import Date, cast, func
from sqlalchemy.orm import Session

from ..database import ActivityEvent, EventCategory
from ..models import (
    ActivityEventCreate,
    AnalyticsSummaryResponse,
    DailyActiveUsersResponse,
    PagePopularityResponse,
    PeakUsageResponse,
    SessionDurationResponse,
    TopicPopularityResponse,
    UserEngagementResponse,
)

"""
Analytics Service - Records and queries user activity events.
Provides aggregated metrics for the admin dashboard.
"""

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for recording and querying activity analytics."""

    def __init__(self, db: Session):
        self.db = db

    def record_events(self, student_id: int, events: list[ActivityEventCreate]) -> int:
        """Batch insert activity events. Returns count of inserted events."""
        db_events = []
        for event in events:
            db_event = ActivityEvent(
                student_id=student_id,
                session_id=event.session_id,
                event_category=event.event_category,
                event_action=event.event_action,
                page_name=event.page_name,
                topic=event.topic,
                timestamp=datetime.now(timezone.utc),
                duration_seconds=event.duration_seconds,
                extra_data=event.extra_data or {},
            )
            db_events.append(db_event)

        self.db.add_all(db_events)
        self.db.commit()
        logger.info(f"Recorded {len(db_events)} activity events for student {student_id}")
        return len(db_events)

    def get_daily_active_users(self, start_date: date, end_date: date) -> DailyActiveUsersResponse:
        """Count distinct student_ids per day."""
        results = (
            self.db.query(
                cast(ActivityEvent.timestamp, Date).label("day"),
                func.count(func.distinct(ActivityEvent.student_id)).label("count"),
            )
            .filter(
                cast(ActivityEvent.timestamp, Date) >= start_date,
                cast(ActivityEvent.timestamp, Date) <= end_date,
            )
            .group_by(cast(ActivityEvent.timestamp, Date))
            .order_by(cast(ActivityEvent.timestamp, Date))
            .all()
        )

        dates = [row.day.isoformat() for row in results]
        counts = [row.count for row in results]
        return DailyActiveUsersResponse(dates=dates, counts=counts)

    def get_avg_session_duration(self, start_date: date, end_date: date) -> SessionDurationResponse:
        """Compute the average session duration per day.

        A session's duration = max(timestamp) - min(timestamp) for each session_id.
        """
        # Subquery: duration per session per day
        session_durations = (
            self.db.query(
                cast(func.min(ActivityEvent.timestamp), Date).label("day"),
                ActivityEvent.session_id,
                (
                    func.extract("epoch", func.max(ActivityEvent.timestamp))
                    - func.extract("epoch", func.min(ActivityEvent.timestamp))
                ).label("duration_secs"),
            )
            .filter(
                cast(ActivityEvent.timestamp, Date) >= start_date,
                cast(ActivityEvent.timestamp, Date) <= end_date,
            )
            .group_by(ActivityEvent.session_id)
            .subquery()
        )

        # Average duration per day (convert to minutes)
        results = (
            self.db.query(
                session_durations.c.day,
                (func.avg(session_durations.c.duration_secs) / 60.0).label("avg_minutes"),
            )
            .group_by(session_durations.c.day)
            .order_by(session_durations.c.day)
            .all()
        )

        dates = [row.day.isoformat() for row in results]
        avg_minutes = [round(float(row.avg_minutes or 0), 2) for row in results]
        return SessionDurationResponse(dates=dates, avg_duration_minutes=avg_minutes)

    def get_peak_usage_hours(self, start_date: date, end_date: date) -> PeakUsageResponse:
        """Count events per hour of the day."""
        results = (
            self.db.query(
                func.extract("hour", ActivityEvent.timestamp).label("hour"),
                func.count(ActivityEvent.id).label("count"),
            )
            .filter(
                cast(ActivityEvent.timestamp, Date) >= start_date,
                cast(ActivityEvent.timestamp, Date) <= end_date,
            )
            .group_by(func.extract("hour", ActivityEvent.timestamp))
            .order_by(func.extract("hour", ActivityEvent.timestamp))
            .all()
        )

        hours = [int(row.hour) for row in results]
        event_counts = [row.count for row in results]
        return PeakUsageResponse(hours=hours, event_counts=event_counts)

    def get_page_popularity(self, start_date: date, end_date: date) -> PagePopularityResponse:
        """Count page_visit events and average duration per page."""
        # Get visit counts
        visit_results = (
            # Queries page visit counts within the date range
            self.db.query(
                ActivityEvent.page_name,
                func.count(ActivityEvent.id).label("visits"),
            )
            .filter(
                ActivityEvent.event_category == EventCategory.PAGE_VISIT,
                ActivityEvent.page_name.isnot(None),
                cast(ActivityEvent.timestamp, Date) >= start_date,
                cast(ActivityEvent.timestamp, Date) <= end_date,
            )
            .group_by(ActivityEvent.page_name)
            .order_by(func.count(ActivityEvent.id).desc())
            .all()
        )

        # Get average duration from page_exit events
        duration_results = (
            # Queries average duration for page exit events
            self.db.query(
                ActivityEvent.page_name,
                func.avg(ActivityEvent.duration_seconds).label("avg_duration"),
            )
            .filter(
                ActivityEvent.event_category == EventCategory.PAGE_EXIT,
                ActivityEvent.page_name.isnot(None),
                ActivityEvent.duration_seconds.isnot(None),
                cast(ActivityEvent.timestamp, Date) >= start_date,
                cast(ActivityEvent.timestamp, Date) <= end_date,
            )
            .group_by(ActivityEvent.page_name)
            .all()
        )

        duration_map = {row.page_name: float(row.avg_duration or 0) for row in duration_results}

        pages = [row.page_name for row in visit_results]
        visit_counts = [row.visits for row in visit_results]
        avg_durations = [round(duration_map.get(page, 0), 1) for page in pages]

        return PagePopularityResponse(
            pages=pages, visit_counts=visit_counts, avg_duration_seconds=avg_durations
        )

    def get_topic_popularity(self, start_date: date, end_date: date) -> TopicPopularityResponse:
        """Count interactions per topic."""
        results = (
            # Queries topic interactions within the date range
            self.db.query(
                ActivityEvent.topic,
                func.count(ActivityEvent.id).label("count"),
            )
            .filter(
                ActivityEvent.topic.isnot(None),
                cast(ActivityEvent.timestamp, Date) >= start_date,
                cast(ActivityEvent.timestamp, Date) <= end_date,
            )
            .group_by(ActivityEvent.topic)
            .order_by(func.count(ActivityEvent.id).desc())
            .all()
        )

        topics = [row.topic for row in results]
        interaction_counts = [row.count for row in results]
        return TopicPopularityResponse(topics=topics, interaction_counts=interaction_counts)

    def get_user_engagement(self, start_date: date, end_date: date) -> UserEngagementResponse:
        """Aggregate engagement metrics over the date range."""
        base_filter = [
            cast(ActivityEvent.timestamp, Date) >= start_date,
            cast(ActivityEvent.timestamp, Date) <= end_date,
        ]

        total_events = (
            self.db.query(func.count(ActivityEvent.id))
            .filter(*base_filter)
            .scalar() or 0
        )

        unique_sessions = (
            self.db.query(func.count(func.distinct(ActivityEvent.session_id)))
            .filter(*base_filter)
            .scalar() or 0
        )

        avg_events_per_session = round(total_events / unique_sessions, 2) if unique_sessions > 0 else 0

        # Average session duration
        session_durations = (
            self.db.query(
                (
                    func.extract("epoch", func.max(ActivityEvent.timestamp))
                    - func.extract("epoch", func.min(ActivityEvent.timestamp))
                ).label("duration_secs"),
            )
            .filter(*base_filter)
            .group_by(ActivityEvent.session_id)
            .subquery()
        )

        avg_duration = (
            self.db.query(func.avg(session_durations.c.duration_secs) / 60.0)
            .scalar()
        )
        avg_session_duration_minutes = round(float(avg_duration or 0), 2)

        total_chat_messages = (
            self.db.query(func.count(ActivityEvent.id))
            .filter(*base_filter, ActivityEvent.event_category == EventCategory.CHAT_MESSAGE)
            .scalar() or 0
        )

        total_assessments_generated = (
            self.db.query(func.count(ActivityEvent.id))
            .filter(*base_filter, ActivityEvent.event_category == EventCategory.ASSESSMENT_GENERATE)
            .scalar() or 0
        )

        total_assessments_submitted = (
            self.db.query(func.count(ActivityEvent.id))
            .filter(*base_filter, ActivityEvent.event_category == EventCategory.ASSESSMENT_SUBMIT)
            .scalar() or 0
        )

        return UserEngagementResponse(
            total_events=total_events,
            unique_sessions=unique_sessions,
            avg_events_per_session=avg_events_per_session,
            avg_session_duration_minutes=avg_session_duration_minutes,
            total_chat_messages=total_chat_messages,
            total_assessments_generated=total_assessments_generated,
            total_assessments_submitted=total_assessments_submitted,
        )

    def get_analytics_summary(self, days: int = 30) -> AnalyticsSummaryResponse:
        """Get a combined analytics summary for the last N days."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        return AnalyticsSummaryResponse(
            dau=self.get_daily_active_users(start_date, end_date),
            session_duration=self.get_avg_session_duration(start_date, end_date),
            peak_usage=self.get_peak_usage_hours(start_date, end_date),
            page_popularity=self.get_page_popularity(start_date, end_date),
            topic_popularity=self.get_topic_popularity(start_date, end_date),
            engagement=self.get_user_engagement(start_date, end_date),
        )


def get_analytics_service(db: Session) -> AnalyticsService:
    """Create an analytics service instance."""
    return AnalyticsService(db)
