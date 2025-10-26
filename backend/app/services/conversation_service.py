from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
import logging

from backend import Message, Conversation, Student
from backend import format_conversation_history, format_knowledge_level_context

logger = logging.getLogger(__name__)

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
                                 include_system: bool = False) -> List[Dict[str, str]]:
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
                            topic: Optional[str] = None,) -> Dict[str, Any]:
        """
        Get student context for personalization.

        Args:
            student_id: Student ID
            topic: Optional topic to get knowledge level for

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
                                 topic: Optional[str] = None,
                                 history_limit: int = 10) -> Dict[str, Any]:
        """
        Get complete context for a conversation.
        Combines conversation history and student information.

        Args:
            conversation_id: Conversation ID
            student_id: Student ID
            topic: Optional topic
            history_limit: Number of recent messages to include

        Returns:
            Dictionary with complete context
        """
        # Get conversation history
        history = self.get_conversation_history(
            conversation_id=conversation_id,
            limit=history_limit
        )

        # Get student context
        student_context = self.get_student_context(
            student_id=student_id,
            topic=topic
        )

        # Combine contexts
        context = {
            "conversation_id": conversation_id,
            "conversation_history": history,
            "student": student_context,
            "topic": topic
        }
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

    def get_recent_topics(self, student_id: int,  limit: int = 5) -> List[str]:
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

    def get_conversation_summary(self, conversation_id: int) -> Optional[str]:
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

            # Check if there's a summary in metadata
            if conversation.metadata and "summary" in conversation.metadata:
                return conversation.metadata["summary"]

            # Get first few messages as summary
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

def get_conversation_service(db: Session) -> ConversationService:
    """
    Create a conversation service instance.

    Args:
        db: Database session

    Returns:
        ConversationService instance
    """
    return ConversationService(db)