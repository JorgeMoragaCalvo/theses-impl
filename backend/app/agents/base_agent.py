from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging
import os
import random

from ..services.llm_service import get_llm_service
from ..utils import (
    format_error_message,
    detect_confusion_signals,
    detect_repeated_topic,
    should_request_feedback
)

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

    async def a_generate_response(self,
                                  user_message: str,
                                  conversation_history: List[Dict[str, str]],
                                  context: Dict[str, Any]) -> str:
        """
        Async version of generate_response.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response string
        """
        try:
            # Get system prompt
            system_prompt = self.get_system_prompt(context)

            # Build messages list
            messages = conversation_history.copy()
            messages.append({"role": "user", "content": user_message})

            # Generate response asynchronously
            response = await self.llm_service.a_generate_response(
                messages=messages,
                system_prompt=system_prompt
            )

            logger.info(
                f"{self.agent_name} (async) generated response: "
                f"{len(response)} chars"
            )

            return response
        except Exception as e:
            logger.error(f"Error in {self.agent_name} (async) response generation: {str(e)}")
            return format_error_message(e)

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about this agent.

        Returns:
            Dictionary with agent information
        """
        return {
            "name": self.agent_name,
            "type": self.agent_type,
            "has_course_materials": self.course_materials is not None,
            "llm_provider": self.llm_service.get_provider_info()
        }

    @staticmethod
    def validate_message(message: str) -> bool:
        """
        Validate the user message before processing.

        Args:
            message: User message

        Returns:
            True if the message is valid
        """
        # Basic validation
        if not message or not message.strip():
            return False

        # Check message length (avoid extremely long messages)
        if len(message) > 1000:
            logger.warning(f"Message too long: {len(message)} chars")
            return False
        return True

    @staticmethod
    def preprocess_message(message: str) -> str:
        """
        Preprocess user message before sending to LLM.

        Args:
            message: Raw user message

        Returns:
            Preprocessed message
        """
        # Remove excessive whitespace
        message = " ".join(message.split())

        # Trim
        message = message.strip()
        return message

    @staticmethod
    def postprocess_response(response: str) -> str:
        """
        Postprocess LLM response before returning to the user.

        Args:
            response: Raw LLM response

        Returns:
            Postprocessed response
        """
        # Basic cleanup
        response = response.strip()
        return response

    # Adaptive Learning & Alternative Explanations Methods

    @staticmethod
    def detect_student_confusion(
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Detect if the student is confused based on the current message and conversation history.

        Args:
            user_message: Current user message
            conversation_history: Previous messages

        Returns:
            Dictionary with confusion analysis (detected, level, signals, repeated_topic)
        """
        # Detect confusion signals in current message
        confusion_analysis = detect_confusion_signals(user_message)

        # Check for repeated topics (indicates struggling)
        repeated_topic_info = detect_repeated_topic(conversation_history)

        # Combine analyses
        result = {
            "detected": confusion_analysis["detected"] or repeated_topic_info["repeated"],
            "level": confusion_analysis["level"],
            "signals": confusion_analysis["signals"],
            "repeated_topic": repeated_topic_info
        }

        # Escalate confusion level if the topic is being repeated
        if repeated_topic_info["repeated"] and repeated_topic_info["count"] >= 3:
            if result["level"] in ["none", "low"]:
                result["level"] = "medium"
                result["signals"].append("repeated_topic_escalation")

        logger.info(
            f"Confusion detection: detected={result['detected']}, "
            f"level={result['level']}, signals={len(result['signals'])}"
        )

        return result

    @staticmethod
    def select_explanation_strategy(
        confusion_level: str,
        knowledge_level: str,
        previous_strategies: List[str],
        all_available_strategies: List[str]
    ) -> str:
        """
        Select the most appropriate explanation strategy based on context.

        Args:
            confusion_level: Detected confusion level (none/low/medium/high)
            knowledge_level: Student's knowledge level (beginner/intermediate/advanced)
            previous_strategies: Recently used strategies
            all_available_strategies: All available strategy options

        Returns:
            Selected strategy name
        """
        # Default strategies by knowledge level
        default_strategies = {
            "beginner": ["step-by-step", "example-based", "analogy-based"],
            "intermediate": ["example-based", "conceptual", "step-by-step"],
            "advanced": ["conceptual", "formal-mathematical", "comparative"]
        }

        # Get preferred strategies for this knowledge level
        preferred = default_strategies.get(knowledge_level, default_strategies["beginner"])

        # Adjust based on the confusion level
        if confusion_level == "high":
            # Use simplest, most concrete strategies
            preferred = ["step-by-step", "example-based", "analogy-based"]
        elif confusion_level == "medium":
            # Mix of concrete and conceptual
            preferred = ["example-based", "step-by-step", "conceptual"]
        # For low/none confusion, use knowledge-level defaults

        # Filter out recently used strategies to provide variety
        recent_set = set(previous_strategies[-3:]) if previous_strategies else set()
        available = [s for s in all_available_strategies if s not in recent_set]

        # If all strategies have been used recently, reset
        if not available:
            available = all_available_strategies

        # Prioritize preferred strategies that are available
        for strategy in preferred:
            if strategy in available:
                logger.info(f"Selected explanation strategy: {strategy} (confusion={confusion_level})")
                return strategy

        # Fallback: pick randomly from available
        selected = random.choice(available)
        logger.info(f"Selected fallback strategy: {selected}")
        return selected

    @staticmethod
    def build_adaptive_prompt_section(
        confusion_analysis: Dict[str, Any],
        selected_strategy: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Build adaptive instructions to inject into system prompt based on confusion analysis.

        Args:
            confusion_analysis: Results from detect_student_confusion()
            selected_strategy: Selected explanation strategy
            context: Full conversation context

        Returns:
            String with adaptive instructions for the LLM
        """
        adaptive_instructions = []

        # Add confusion-specific instructions
        if confusion_analysis["detected"]:
            confusion_level = confusion_analysis["level"]

            if confusion_level == "high":
                adaptive_instructions.append(
                    "⚠️ IMPORTANT: The student appears to be significantly confused or lost. "
                    "ACKNOWLEDGE their confusion empathetically, then SIMPLIFY your explanation dramatically. "
                    "Break down the concept into the smallest possible steps. "
                    "Use concrete examples with real numbers. Avoid jargon and technical terminology."
                )
            elif confusion_level == "medium":
                adaptive_instructions.append(
                    "📌 NOTICE: The student seems uncertain or unclear about the concept. "
                    "ACKNOWLEDGE this and offer a different perspective. "
                    "Try explaining with a practical example or walking through step-by-step. "
                    "Check their understanding as you go."
                )
            elif confusion_level == "low":
                adaptive_instructions.append(
                    "💡 NOTE: The student might need clarification. "
                    "Be ready to rephrase or provide additional context. "
                    "Ask if they need more explanation on any specific part."
                )

        # Add repeated topic instructions
        if confusion_analysis.get("repeated_topic", {}).get("repeated"):
            topic = confusion_analysis["repeated_topic"].get("topic", "this concept")
            adaptive_instructions.append(
                f"🔄 The student has asked about '{topic}' multiple times. "
                f"They may be stuck on this specific concept. "
                f"Try a completely DIFFERENT APPROACH than before. "
                f"Consider using an analogy, a visual description, or a step-by-step breakdown."
            )

        # Add strategy-specific instructions
        strategy_prompts = {
            "step-by-step": (
                "📝 Use a STEP-BY-STEP approach: Break down the concept into numbered sequential steps. "
                "Explain what happens at each step and why. Make each step clear and actionable."
            ),
            "example-based": (
                "📊 Use an EXAMPLE-BASED approach: Provide a concrete, numerical example. "
                "Work through the example completely, showing all calculations. "
                "Then explain how the example demonstrates the general concept."
            ),
            "conceptual": (
                "💭 Use a CONCEPTUAL approach: Focus on the underlying ideas and intuition. "
                "Explain the 'why' behind the concept before the 'how'. "
                "Help build understanding of the big picture."
            ),
            "analogy-based": (
                "🌟 Use an ANALOGY or METAPHOR approach: Relate the concept to something familiar from everyday life. "
                "Draw parallels that make the abstract concrete. "
                "Then connect the analogy back to the mathematical concept."
            ),
            "visual": (
                "🎨 Use a VISUAL/GEOMETRIC approach: Describe what this would look like graphically. "
                "Paint a picture with words - explain shapes, regions, lines, points. "
                "Help the student visualize the concept spatially."
            ),
            "formal-mathematical": (
                "🔬 Use a FORMAL MATHEMATICAL approach: Provide rigorous definitions and mathematical notation. "
                "Show the theoretical foundations. Explain with precision and mathematical exactness."
            ),
            "comparative": (
                "⚖️ Use a COMPARATIVE approach: Compare and contrast with related concepts or methods. "
                "Highlight similarities and differences. "
                "Show when to use this approach versus alternatives."
            )
        }

        if selected_strategy in strategy_prompts:
            adaptive_instructions.append(f"🎯 EXPLANATION STRATEGY: {strategy_prompts[selected_strategy]}")

        # Combine all instructions
        if adaptive_instructions:
            header = "\n" + "=" * 80 + "\n🤖 ADAPTIVE TEACHING MODE ACTIVATED\n" + "=" * 80 + "\n"
            footer = "\n" + "=" * 80 + "\n"
            return header + "\n\n".join(adaptive_instructions) + footer

        return ""

    @staticmethod
    def should_add_feedback_request(
        response_text: str,
        conversation_history: List[Dict[str, str]],
        context: Dict[str, Any],
        confusion_detected: bool
    ) -> bool:
        """
        Determine if a feedback request should be added to the response.

        Args:
            response_text: Generated response
            conversation_history: Conversation history
            context: Context dictionary
            confusion_detected: Whether confusion was detected

        Returns:
            True if feedback should be requested
        """
        # Update context with confusion info
        context["recent_confusion_detected"] = confusion_detected

        return should_request_feedback(response_text, conversation_history, context)

    @staticmethod
    def add_feedback_request_to_response(
        response: str,
        confusion_level: str,
        selected_strategy: str
    ) -> str:
        """
        Append an understanding check-in to the response.

        Args:
            response: Generated response text
            confusion_level: Detected confusion level
            selected_strategy: Strategy used for explanation

        Returns:
            Response with feedback request appended
        """
        feedback_prompts = {
            "high": [
                "\n\nDoes this explanation make more sense? If anything is still unclear, please let me know and I'll try explaining it a different way.",
                "\n\nI want to make sure this is clear. Can you tell me if this makes sense, or if you'd like me to explain any part differently?",
            ],
            "medium": [
                "\n\nDoes that help clarify things? Feel free to ask if you need more explanation on any part.",
                "\n\nIs this clearer now? Let me know if you'd like me to elaborate on anything.",
            ],
            "low": [
                "\n\nDoes this answer your question? Happy to provide more details if needed.",
                "\n\nLet me know if you'd like me to explain anything further!",
            ],
            "none": [
                "\n\nFeel free to ask if you'd like more examples or a different explanation approach!",
                "\n\nLet me know if you'd like to explore this further or try a practice problem!",
            ]
        }

        # For high/medium confusion, offer explicit alternative options
        if confusion_level in ["high", "medium"]:
            prompts = feedback_prompts.get(confusion_level, feedback_prompts["none"])
            prompt = random.choice(prompts)

            # Add alternative approach options for high confusion
            if confusion_level == "high":
                prompt += "\n\nI can explain this using:\n- A concrete example with numbers\n- A step-by-step breakdown\n- An analogy to something familiar\n\nWhich would help you most?"

        else:
            prompts = feedback_prompts.get(confusion_level, feedback_prompts["none"])
            prompt = random.choice(prompts)

        return response + prompt