from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
import logging

from ...database import Message, Conversation, Student
from ...utils import format_conversation_history, format_knowledge_level_context

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

            # Get knowledge level for topic
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