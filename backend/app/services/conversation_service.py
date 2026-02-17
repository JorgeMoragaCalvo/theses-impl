import logging
from typing import Any

from sqlalchemy.orm import Session

from ..database import Assessment, Conversation, Message, Student
from ..models import ProgressResponse
from ..utils import format_conversation_history, format_knowledge_level_context

logger = logging.getLogger(__name__)


def _sanitize_for_log(value: Any) -> str:
    """
    Sanitize a value for safe logging by removing line breaks.

    This helps prevent log injection when logging user-controlled data.
    """
    text = str(value)
    # Remove common line break sequences
    return text.replace("\r\n", "").replace("\n", "").replace("\r", "")


class ConversationService:
    """Service for managing conversation context and history."""
    def __init__(self, db: Session):
        """
        Initialize conversation service.

        Args:
            db: Database session
        """
        self.db = db

    def get_conversation_history(self, conversation_id: int,
                                 limit: int = 10,
                                 include_system: bool = False) -> list[dict[str, str]]:
        """
        Get recent messages from a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve
            include_system: Whether to include system messages

        Returns:
            List of message dictionaries formatted for LLM
        """
        try:
            # Query messages
            query = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            )

            # Optionally exclude system messages
            if not include_system:
                query = query.filter(Message.role != 'system')

            # Get most recent messages, ordered by timestamp
            messages = query.order_by(
                Message.timestamp.desc()
            ).limit(limit).all()

            # Reverse to get chronological order
            messages = list(reversed(messages))

            # Format for LLM
            formatted_messages = format_conversation_history(messages)

            logger.info(f"Retrieved {len(formatted_messages)} messages from conversation {conversation_id}")
            return formatted_messages
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []

    def get_student_context(self, student_id: int,
                            topic: str | None = None,
                            include_assessment_data: bool = True) -> dict[str, Any]:
        """
        Get student context for personalization.

        Args:
            student_id: Student ID
            topic: Optional topic to get knowledge level for
            include_assessment_data: Whether to include assessment performance data

        Returns:
            Dictionary with student context
        """
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()

            if not student:
                logger.warning(f"Student {student_id} not found ")
                return {
                    "knowledge_level": "beginner",
                    "knowledge_level_description": format_knowledge_level_context("beginner"),
                    "preferences": {}
                }

            # Get knowledge level for the topic
            knowledge_level = "beginner"
            if topic and student.knowledge_levels:
                knowledge_level = student.knowledge_levels.get(topic, "beginner")

            context = {
                "student_id": student_id,
                "student_name": student.name,
                "knowledge_level": knowledge_level,
                "knowledge_level_description": format_knowledge_level_context(knowledge_level),
                "preferences": student.preferences or {},
                "all_knowledge_levels": student.knowledge_levels or {}
            }

            # Add assessment data if requested
            if include_assessment_data:
                # Get assessment performance summary
                performance = self.get_assessment_performance_summary(student_id, topic)
                context["assessment_performance"] = performance

                # Get recent assessment scores for context
                recent_assessments = self.get_student_assessment_history(student_id, topic, limit=3)
                context["recent_assessment_scores"] = [
                    {"score": a.score, "max_score": a.max_score, "feedback_summary": a.feedback[:50] if a.feedback else None}
                    for a in recent_assessments if a.score is not None
                ]

                # Get knowledge gaps if the topic is specified
                if topic:
                    knowledge_gaps = self.get_knowledge_gaps_from_assessments(student_id, topic)
                    context["knowledge_gaps"] = knowledge_gaps

                    # Add competency context
                    competency_context = self.get_student_competency_context(student_id, topic)
                    if competency_context:
                        context["competency_context"] = competency_context

            logger.info(f"Retrieved student context for student {student_id}: level={knowledge_level}")
            return context
        except Exception as e:
            logger.error(f"Error retrieving student context: {str(e)}")
            return {
                "knowledge_level": "beginner",
                "knowledge_level_description": format_knowledge_level_context("beginner"),
                "preferences": {}
            }

    def get_conversation_context(self, conversation_id: int,
                                 student_id: int,
                                 topic: str | None = None,
                                 history_limit: int = 10,
                                 include_assessment_data: bool = True) -> dict[str, Any]:
        """
        Get complete context for a conversation.
        Combines conversation history, student information, assessment data, and adaptive learning metadata.

        Args:
            conversation_id: Conversation ID
            student_id: Student ID
            topic: Optional topic
            history_limit: Number of recent messages to include
            include_assessment_data: Whether to include assessment context

        Returns:
            Dictionary with complete context
        """
        # Get conversation history
        history = self.get_conversation_history(
            conversation_id=conversation_id,
            limit=history_limit
        )

        # Get student context (with assessment data if requested)
        student_context = self.get_student_context(
            student_id=student_id,
            topic=topic,
            include_assessment_data=include_assessment_data
        )

        # Get conversation extra_data for adaptive learning metadata
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        conversation_extra_data = {}
        if conversation and conversation.extra_data:
            conversation_extra_data = conversation.extra_data

        # Combine contexts
        context = {
            "conversation_id": conversation_id,
            "conversation_history": history,
            "student": student_context,
            "topic": topic,
            "conversation_extra_data": conversation_extra_data
        }

        # Add assessment-specific context if requested and the topic is provided
        if include_assessment_data and topic:
            # Get topic-specific assessment history
            topic_assessments = self.get_student_assessment_history(student_id, topic, limit=3)
            context["topic_assessment_history"] = [
                {
                    "question": a.question[:100] if a.question else None,
                    "score": a.score,
                    "max_score": a.max_score,
                    "feedback": a.feedback[:100] if a.feedback else None,
                    "created_at": a.created_at.isoformat() if a.created_at else None
                }
                for a in topic_assessments
            ]

            # Check if assessment should be suggested
            context["should_suggest_assessment"] = self.should_suggest_assessment(
                conversation_id, student_id, topic
            )

        return context

    def count_conversation_messages(self, conversation_id: int) -> int:
        """
        Count total messages in a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            Number of messages
        """
        try:
            count = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).count()

            return count
        except Exception as e:
            logger.error(f"Error counting conversation messages: {str(e)}")
            return 0

    def get_recent_topics(self, student_id: int,  limit: int = 5) -> list[str]:
        """
        Get recently discussed topics for a student.

        Args:
            student_id: Student ID
            limit: Number of recent topics

        Returns:
            List of topic names
        """
        try:
            # Get recent conversations with topics
            conversations = self.db.query(Conversation).filter(
                Conversation.student_id == student_id,
                Conversation.topic.isnot(None)
            ).order_by(
                Conversation.started_at.desc()
            ).limit(limit).all()

            topics = [conv.topic.value for conv in conversations if conv.topic]
            return topics
        except Exception as e:
            logger.error(f"Error retrieving recent topics: {str(e)}")
            return []

    def is_new_conversation(self, conversation_id: int) -> bool:
        """
        Check if a conversation is new (has few messages).

        Args:
            conversation_id: Conversation ID

        Returns:
            True if the conversation has 2 or fewer messages
        """
        message_count = self.count_conversation_messages(conversation_id)
        return message_count <= 2

    def get_conversation_summary(self, conversation_id: int) -> str | None:
        """
        Get a brief summary of what the conversation is about.

        Args:
            conversation_id: Conversation ID

        Returns:
            Summary string or None
        """
        try:
            # Get conversation metadata
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                return None

            # Check if there's a summary in extra_data
            if conversation.extra_data and "summary" in conversation.extra_data:
                return conversation.extra_data["summary"]

            # Get the first few messages as a summary
            messages = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp).limit(3).all()

            if not messages:
                return "New conversation"

            # Create the basic summary from the first user message
            first_user_msg = next((m for m in messages if m.role == "user"), None)
            if first_user_msg:
                content = first_user_msg.content[:100]
                return f"Discussion about: {content}..."

            return "Ongoing conversation"
        except Exception as e:
            logger.error(f"Error getting conversation summary: {str(e)}")
            return None

    def get_student_assessment_history(self, student_id: int,
                                       topic: str | None = None,
                                       limit: int = 5) -> list[Assessment]:
        """
        Get recent assessments for a student.

        Args:
            student_id: Student ID
            topic: Optional topic to filter by
            limit: Number of recent assessments to retrieve

        Returns:
            List of Assessment objects
        """
        try:
            query = self.db.query(Assessment).filter(
                Assessment.student_id == student_id
            )

            # Filter by topic if provided
            if topic:
                query = query.filter(Assessment.topic == topic)

            # Get most recent assessments
            assessments = query.order_by(
                Assessment.created_at.desc()
            ).limit(limit).all()

            logger.info(f"Retrieved {len(assessments)} assessments for student {student_id}")
            return assessments
        except Exception as e:
            logger.error(f"Error retrieving assessment history: {str(e)}")
            return []

    def get_assessment_performance_summary(self, student_id: int,
                                           topic: str | None = None) -> dict[str, Any]:
        """
        Get aggregate assessment performance statistics for a student.

        Args:
            student_id: Student ID
            topic: Optional topic to filter by

        Returns:
            Dictionary with performance metrics
        """
        try:
            query = self.db.query(Assessment).filter(
                Assessment.student_id == student_id
            )

            # Filter by topic if provided
            if topic:
                query = query.filter(Assessment.topic == topic)

            assessments = query.all()

            # Calculate statistics
            total_assessments = len(assessments)
            graded_assessments = [a for a in assessments if a.score is not None]
            completed_assessments = [a for a in assessments if a.submitted_at is not None]

            average_score = None
            if graded_assessments:
                average_score = sum(a.score for a in graded_assessments) / len(graded_assessments)

            completion_rate = None
            if total_assessments > 0:
                completion_rate = len(completed_assessments) / total_assessments

            summary = {
                "total_assessments": total_assessments,
                "completed_assessments": len(completed_assessments),
                "graded_assessments": len(graded_assessments),
                "average_score": round(average_score, 2) if average_score else None,
                "completion_rate": round(completion_rate, 2) if completion_rate else None,
                "recent_scores": [a.score for a in graded_assessments[-5:]] if graded_assessments else []
            }

            logger.info(f"Assessment performance summary for student {student_id}: "
                       f"avg_score={summary['average_score']}, total={total_assessments}")
            return summary
        except Exception as e:
            logger.error(f"Error calculating assessment performance: {str(e)}")
            return {
                "total_assessments": 0,
                "completed_assessments": 0,
                "graded_assessments": 0,
                "average_score": None,
                "completion_rate": None,
                "recent_scores": []
            }

    def get_knowledge_gaps_from_assessments(self, student_id: int,
                                            topic: str) -> list[str]:
        """
        Identify knowledge gaps based on assessment feedback and performance.

        Args:
            student_id: Student ID
            topic: Topic to analyze

        Returns:
            List of concepts/areas where the student struggles
        """
        try:
            # Get assessments for the topic
            assessments = self.db.query(Assessment).filter(
                Assessment.student_id == student_id,
                Assessment.topic == topic
            ).order_by(Assessment.created_at.desc()).all()

            knowledge_gaps = []

            for assessment in assessments:
                # Look for low scores
                if assessment.score is not None and assessment.max_score:
                    score_percentage = (assessment.score / assessment.max_score) * 100
                    if score_percentage < 60:  # Below 60% indicates struggle
                        # Extract feedback that indicates gaps
                        if assessment.feedback:
                            knowledge_gaps.append(f"Low score ({score_percentage:.0f}%): {assessment.feedback[:100]}")

                # Check if incomplete or not submitted
                if assessment.created_at and not assessment.submitted_at:
                    knowledge_gaps.append(f"Incomplete assessment: {assessment.question[:100]}")

            # Remove duplicates and limit
            unique_gaps = list(set(knowledge_gaps))[:5]

            safe_student_id = _sanitize_for_log(student_id)
            safe_topic = _sanitize_for_log(topic)
            logger.info(f"Identified {len(unique_gaps)} knowledge gaps for student {safe_student_id} in {safe_topic}")
            return unique_gaps
        except Exception as e:
            logger.error(f"Error identifying knowledge gaps: {str(e)}")
            return []

    def get_student_competency_context(
        self, student_id: int, topic: str
    ) -> dict[str, Any]:
        """
        Get a concise mastery context for injection into agent prompts.

        Args:
            student_id: Student ID
            topic: Topic string

        Returns:
            Dictionary with mastery_summary, weak_concepts, and next_concepts keys
        """
        try:
            from .competency_service import get_competency_service
            competency_service = get_competency_service(self.db)
            summary = competency_service.get_mastery_summary(student_id, topic)
            next_concepts = competency_service.get_next_concepts_to_learn(student_id, topic)

            weak_concepts = [
                c for c in summary.get("concepts", [])
                if c["mastery_level"] in ("novice", "developing") and c["attempts_count"] > 0
            ][:5]

            return {
                "mastery_summary": {
                    "average_score": summary.get("average_mastery_score", 0.0),
                    "level_counts": summary.get("level_counts", {}),
                },
                "weak_concepts": weak_concepts,
                "next_concepts_to_learn": next_concepts[:3],
            }
        except Exception as e:
            logger.error(f"Error fetching competency context for student {student_id}: {e}")
            return {}

    def compute_student_progress(self, student_id: int) -> ProgressResponse:
        """
        Compute comprehensive student progress metrics.

        Args:
            student_id: Student ID

        Returns:
            ProgressResponse with aggregated metrics
        """
        safe_student_id = _sanitize_for_log(student_id)

        logger.info(f"Computing progress for student {safe_student_id}")

        # Get student info
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                logger.warning(f"Student {safe_student_id} not found for progress computation")
                return ProgressResponse(
                    student_id=student_id,
                    knowledge_levels={},
                    total_conversations=0,
                    total_messages=0,
                    total_assessments=0,
                    topics_covered=[],
                    recent_activity=[]
                )
        except Exception as e:
            logger.error("Error fetching student %s: %s", safe_student_id, str(e))
            return ProgressResponse(
                student_id=student_id,
                knowledge_levels={},
                total_conversations=0,
                total_messages=0,
                total_assessments=0,
                topics_covered=[],
                recent_activity=[]
            )

        # Count conversations (with error handling)
        total_conversations = 0
        try:
            total_conversations = self.db.query(Conversation).filter(
                Conversation.student_id == student_id
            ).count()
            logger.debug(f"Student {safe_student_id}: {total_conversations} conversations")
        except Exception as e:
            logger.error(f"Error counting conversations for student {safe_student_id}: {str(e)}")

        # Count messages (with error handling)
        total_messages = 0
        try:
            total_messages = self.db.query(Message).join(Conversation).filter(
                Conversation.student_id == student_id
            ).count()
            logger.debug(f"Student {safe_student_id}: {total_messages} messages")
        except Exception as e:
            logger.error(f"Error counting messages for student {safe_student_id}: {str(e)}")

        # Get assessments (with error handling)
        total_assessments = 0
        average_score = None
        safe_student_id = _sanitize_for_log(student_id)
        try:
            logger.debug(f"Querying assessments for student {safe_student_id}")
            assessments = self.db.query(Assessment).filter(
                Assessment.student_id == student_id
            ).all()

            total_assessments = len(assessments)
            logger.debug(f"Student {safe_student_id}: {total_assessments} assessments found")

            graded_assessments = [a for a in assessments if a.score is not None]

            # Calculate average score
            if graded_assessments:
                # Filter out None scores before summing (defensive check)
                valid_scores = [a.score for a in graded_assessments if a.score is not None]
                if valid_scores:
                    average_score = sum(valid_scores) / len(valid_scores)
                    logger.debug(f"Student {safe_student_id}: average score = {average_score}")
        except Exception as e:
            logger.error(f"Error processing assessments for student {safe_student_id}: {str(e)}", exc_info=True)

        # Get topics covered from conversations (with error handling)
        topics_covered = []
        try:
            conversations_with_topics = self.db.query(Conversation).filter(
                Conversation.student_id == student_id,
                Conversation.topic.isnot(None)
            ).all()

            topics_covered = list(set([
                conv.topic.value for conv in conversations_with_topics if conv.topic
            ]))
            logger.debug(f"Student {safe_student_id}: {len(topics_covered)} topics covered")
        except Exception as e:
            logger.error(f"Error getting topics for student {safe_student_id}: {str(e)}")

        # Build recent activity timeline (with error handling)
        recent_activity = []
        try:
            # Get recent conversations (last 5)
            recent_conversations = self.db.query(Conversation).filter(
                Conversation.student_id == student_id
            ).order_by(Conversation.started_at.desc()).limit(5).all()

            for conv in recent_conversations:
                try:
                    activity_entry = {
                        "type": "conversation",
                        "timestamp": conv.started_at.isoformat() if conv.started_at else None,
                        "topic": conv.topic.value if conv.topic else "General",
                        "message_count": self.count_conversation_messages(conv.id)
                    }
                    recent_activity.append(activity_entry)
                except Exception as e:
                    logger.warning(f"Error processing conversation {conv.id} for activity: {str(e)}")

            # Get recent assessments (last 5)
            recent_assessments = self.db.query(Assessment).filter(
                Assessment.student_id == student_id
            ).order_by(Assessment.created_at.desc()).limit(5).all()

            for assessment in recent_assessments:
                try:
                    activity_entry = {
                        "type": "assessment",
                        "timestamp": assessment.created_at.isoformat() if assessment.created_at else None,
                        "topic": assessment.topic.value if assessment.topic else "Unknown",
                        "score": assessment.score,
                        "status": "graded" if assessment.graded_at else ("submitted" if assessment.submitted_at else "pending")
                    }
                    recent_activity.append(activity_entry)
                except Exception as e:
                    logger.warning(f"Error processing assessment {assessment.id} for activity: {str(e)}")

            # Sort recent activity by timestamp
            recent_activity.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            recent_activity = recent_activity[:10]  # Keep only 10 most recent
        except Exception as e:
            logger.error(f"Error building recent activity for student {safe_student_id}: {str(e)}")

        # Build response with whatever data we successfully collected
        progress = ProgressResponse(
            student_id=student_id,
            knowledge_levels=student.knowledge_levels or {},
            total_conversations=total_conversations,
            total_messages=total_messages,
            total_assessments=total_assessments,
            average_score=round(average_score, 2) if average_score else None,
            topics_covered=topics_covered,
            recent_activity=recent_activity
        )

        logger.info(f"Computed progress for student {safe_student_id}: "
                   f"{total_conversations} convs, {total_messages} msgs, "
                   f"{total_assessments} assessments, avg_score={average_score}")
        return progress

    def should_suggest_assessment(self, conversation_id: int,
                                   student_id: int,
                                   topic: str) -> bool:
        """
        Determine if the student is ready for an assessment based on conversation activity.

        Args:
            conversation_id: Current conversation ID
            student_id: Student ID
            topic: Topic being discussed

        Returns:
            True if assessment should be suggested
        """
        try:
            # Count messages in this conversation
            message_count = self.count_conversation_messages(conversation_id)

            # Don't suggest in very new conversations
            if message_count < 5:
                return False

            # Check if the student has the recent assessment for this topic
            recent_assessments = self.db.query(Assessment).filter(
                Assessment.student_id == student_id,
                Assessment.topic == topic
            ).order_by(Assessment.created_at.desc()).limit(1).all()

            # If no assessments yet and conversation is significant, suggest
            if not recent_assessments and message_count >= 10:
                logger.info(f"Suggesting assessment for student {student_id}: no prior assessments, {message_count} messages")
                return True

            # If the last assessment was a while ago (check conversation count)
            if recent_assessments:
                last_assessment = recent_assessments[0]
                # Count conversations since last assessment
                conversations_since = self.db.query(Conversation).filter(
                    Conversation.student_id == student_id,
                    Conversation.topic == topic,
                    Conversation.started_at > last_assessment.created_at
                ).count()

                # Suggest if 3+ conversations since last assessment
                if conversations_since >= 3:
                    logger.info(f"Suggesting assessment for student {student_id}: {conversations_since} conversations since last assessment")
                    return True

            return False
        except Exception as e:
            logger.error(f"Error checking assessment suggestion: {str(e)}")
            return False

    def track_explanation_strategy(
        self,
        conversation_id: int,
        strategy: str,
        confusion_level: str
    ) -> None:
        """
        Track the usage of an explanation strategy in a conversation.

        Args:
            conversation_id: Conversation ID
            strategy: Strategy name used
            confusion_level: Confusion level detected
        """
        try:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found for strategy tracking")
                return

            # Initialize extra_data if needed
            if not conversation.extra_data:
                conversation.extra_data = {}

            # Track strategies used
            strategies_used = conversation.extra_data.get("strategies_used", [])
            strategies_used.append(strategy)
            conversation.extra_data["strategies_used"] = strategies_used

            # Track last strategy
            conversation.extra_data["last_strategy"] = strategy

            # Track confusion count
            if confusion_level in ["low", "medium", "high"]:
                confusion_count = conversation.extra_data.get("confusion_count", 0)
                conversation.extra_data["confusion_count"] = confusion_count + 1

            # Commit changes
            self.db.commit()

            logger.info(
                f"Tracked strategy '{strategy}' for conversation {conversation_id}, "
                f"confusion={confusion_level}"
            )
        except Exception as e:
            logger.error(f"Error tracking explanation strategy: {str(e)}")
            self.db.rollback()

    def mark_strategy_successful(
        self,
        conversation_id: int,
        strategy: str
    ) -> None:
        """
        Mark a strategy as successful (confusion was resolved).

        Args:
            conversation_id: Conversation ID
            strategy: Strategy that was successful
        """
        try:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                return

            # Initialize extra_data if needed
            if not conversation.extra_data:
                conversation.extra_data = {}

            # Track successful strategies
            successful_strategies = conversation.extra_data.get("successful_strategies", {})
            successful_strategies[strategy] = successful_strategies.get(strategy, 0) + 1
            conversation.extra_data["successful_strategies"] = successful_strategies

            # Commit changes
            self.db.commit()

            logger.info(f"Marked strategy '{strategy}' as successful for conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Error marking strategy successful: {str(e)}")
            self.db.rollback()

    def analyze_strategy_effectiveness(
        self,
        conversation_id: int
    ) -> dict[str, Any]:
        """
        Analyze which strategies have been most effective in this conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            Dictionary with strategy effectiveness analysis
        """
        try:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation or not conversation.extra_data:
                return {
                    "strategies_used": [],
                    "successful_strategies": {},
                    "confusion_count": 0,
                    "most_effective": None
                }

            strategies_used = conversation.extra_data.get("strategies_used", [])
            successful_strategies = conversation.extra_data.get("successful_strategies", {})
            confusion_count = conversation.extra_data.get("confusion_count", 0)

            # Find the most effective strategy
            most_effective = None
            if successful_strategies:
                most_effective = max(successful_strategies.items(), key=lambda x: x[1])[0]

            return {
                "strategies_used": strategies_used,
                "successful_strategies": successful_strategies,
                "confusion_count": confusion_count,
                "most_effective": most_effective,
                "total_strategies": len(strategies_used),
                "unique_strategies": len(set(strategies_used))
            }
        except Exception as e:
            logger.error(f"Error analyzing strategy effectiveness: {str(e)}")
            return {
                "strategies_used": [],
                "successful_strategies": {},
                "confusion_count": 0,
                "most_effective": None
            }


def get_conversation_service(db: Session) -> ConversationService:
    """
    Create a conversation service instance.

    Args:
        db: Database session

    Returns:
        ConversationService instance
    """
    return ConversationService(db)
