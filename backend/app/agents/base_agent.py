from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging
import os

from ..services.llm_service import get_llm_service
from backend import format_error_message

"""
Base Agent - Foundation class for all specialized agents.
"""

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Provides common functionality for agent implementations.
    """

    def __init__(self, agent_name: str, agent_type: str):
        """
        Initialize base agent.

        Args:
            agent_name: Human-readable agent name
            agent_type: Agent type identifier
        """
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.llm_service = get_llm_service()
        self.course_materials: Optional[str] = None

        logger.info(f"Initialized {self.agent_name} ({self.agent_type})")

    @abstractmethod
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate system prompt for this agent.
        Must be implemented by subclasses.

        Args:
            context: Context dictionary with student info, knowledge level, etc.

        Returns:
            System prompt string
        """
        pass

    def load_course_materials(self, file_path: str) -> bool:
        """
        Load course materials from a file.

        Args:
            file_path: Path to the course materials file

        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Course materials file not found: {file_path}")
                return False

            with open(file_path, encoding='utf-8') as f:
                self.course_materials = f.read()

            logger.info(f"Loaded course materials from {file_path} ({len(self.course_materials)} chars)")
            return True
        except Exception as e:
            logger.error(f"Error loading course materials: {str(e)}")
            return False

    def format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """
        Format context information for inclusion in prompts.

        Args:
            context: Context dictionary

        Returns:
            Formatted context string
        """
        student = context.get("student", {})
        knowledge_level = student.get("knowledge_level", "beginner")
        knowledge_desc = student.get("knowledge_level_description", "")

        context_parts = []

        # Student knowledge level
        if knowledge_level and knowledge_desc:
            context_parts.append(f"Student knowledge level: {knowledge_level.upper()}")
            context_parts.append(knowledge_desc)

        # Course materials if available
        if self.course_materials:
            context_parts.append("\n--- Course Materials Reference ---")
            # Include the first part of materials (to avoid token limits)
            material_excerpt = self.course_materials[:2000]
            if len(self.course_materials) > 2000:
                material_excerpt += "\n... [additional materials available]"
            context_parts.append(material_excerpt)

        return "\n\n".join(context_parts)

    def generate_response(self, user_message: str,
                          conversation_history: List[Dict[str, str]],
                          context: Dict[str, Any]) -> str:
        """
        Generate agent response to the user message.

        Args:
            user_message: Current user message
            conversation_history: Previous messages in conversation
            context: Context dictionary with student info, etc.

        Returns:
            Generated response string

        Raises:
            Exception: If response generation fails
        """
        try:
            # Get system prompt
            system_prompt = self.get_system_prompt(context)

            # Build messages list
            messages = conversation_history.copy()
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = self.llm_service.generate_response(
                messages=messages,
                system_prompt=system_prompt
            )

            logger.info(
                f"{self.agent_name} generated response: "
                f"{len(response)} chars for message '{user_message[:50]}...'"
            )
            return response
        except Exception as e:
            logger.error(f"Error in {self.agent_name} response generation: {str(e)}")
            return format_error_message(e)