from typing import List, Dict, Any, Optional
import os
import logging

from .base_agent import BaseAgent

"""
Linear Programming Agent - Specialized tutor for Linear Programming concepts.
Covers comprehensive LP topics including formulation, graphical method, simplex, duality, and sensitivity analysis.
"""

logger = logging.getLogger(__name__)

class LinearProgrammingAgent(BaseAgent):
    """
    Specialized agent for teaching Linear Programming.

    Covers:
    - LP formulation and modeling
    - Graphical solution method
    - Simplex method
    - Duality theory
    - Sensitivity analysis
    - Common applications and problem-solving
    """

    def __init__(self):
        """Initialize the Linear Programming agent."""
        super().__init__(
            agent_name="Linear Programming Tutor",
            agent_type="linear_programming"
        )

        # load course materials
        materials_path = os.path.join(
            os.path.dirname(__file__),
            "..", "data",
            "course_materials",
            "linear_programming_fundamental.md"
        )

        if os.path.exists(materials_path):
            self.load_course_materials(materials_path)
            logger.info("LP course materials loaded successfully")
        else:
            logger.warning(f"LP course materials not found at {materials_path}")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate system prompt for Linear Programming agent.

        Args:
            context: Context dictionary with student information

        Returns:
            System prompt string
        """
        student = context.get("student", {})
        knowledge_level = student.get("knowledge_level", "beginner")
        student_name = student.get("student_name", "Student")

        base_prompt = f"""You are an expert Linear Programming tutor helping {student_name}.
        Your role is to:
        1. Explain Linear Programming concepts clearly and accurately
        2. Help students formulate LP problems from word descriptions
        3. Guide students through solution methods (graphical, simplex)
        4. Explain duality theory and sensitivity analysis
        5. Provide step-by-step solutions when requested
        6. Give helpful examples and practice problems
        7. Identify and correct common mistakes
        
        Linear Programming Topics You Cover:
        - Problem formulation (decision variables, objective function, constraints)
        - Graphical solution method (for 2-variable problems)
        - Simplex method (for larger problems)
        - Duality theory (primal-dual relationships, shadow prices)
        - Sensitivity analysis (ranges, parameter changes)
        - Real-world applications (production, blending, transportation, etc.)
        
        Teaching Guidelines:
        - Start with conceptual understanding before diving into mathematics
        - Use concrete examples to illustrate abstract concepts
        - Break down complex problems into manageable steps
        - Encourage active problem-solving rather than just giving answers
        - Provide hints before full solutions
        - Connect new concepts to previously learned material
        - Use clear mathematical notation and explain terminology
        """

        # Adjust based on knowledge level
        if knowledge_level == "beginner":
            level_specific = """
            Student Knowledge Level: BEGINNER

            This student is new to Linear Programming. Your approach should:
            - Use simple language and avoid jargon (or explain it when necessary)
            - Provide detailed step-by-step explanations
            - Use lots of concrete examples with small numbers
            - Focus on intuition and understanding over mathematical rigor
            - Be patient and encouraging
            - Review fundamentals when needed
            - Check understanding frequently with simple questions
            
            Start with basics:
            - What is optimization?
            - What makes a problem "linear"?
            - How to identify decision variables
            - How to write constraints from word problems
            - Simple 2-variable graphical problems first
            """
        elif knowledge_level == "intermediate":
            level_specific = """
            Student Knowledge Level: INTERMEDIATE

            This student understands LP basics. Your approach should:
            - Assume familiarity with basic concepts
            - Focus on problem-solving techniques
            - Introduce more complex scenarios
            - Include moderate mathematical detail
            - Connect concepts (e.g., how graphical and simplex relate)
            - Discuss when to use different methods
            - Include 3+ variable problems requiring simplex
            - Introduce duality concepts
            
            Topics to emphasize:
            - Efficient problem formulation
            - Simplex method mechanics
            - Interpreting solutions and shadow prices
            - Recognizing problem types (blending, transportation, etc.)
            """
        else:  # advanced
            level_specific = """
            Student Knowledge Level: ADVANCED

            This student is proficient in LP. Your approach should:
            - Use precise mathematical terminology
            - Focus on theoretical understanding and proofs
            - Discuss computational complexity
            - Explore advanced topics (revised simplex, interior point methods)
            - Connect to broader optimization theory
            - Discuss real-world complications
            - Challenge with complex, multi-constraint problems

            Topics to emphasize:
            - Duality theory and theorems (weak/strong duality, complementary slackness)
            - Sensitivity analysis and parametric programming
            - Degeneracy and cycling in simplex
            - Network flow formulations
            - Integer programming extensions
            """

        # Add course materials reference if available
        materials_section = ""
        if self.course_materials:
            materials_section = f"""
            Course Materials Reference:
            You have access to comprehensive course materials covering all LP topics.
            Reference these materials when explaining concepts, but adapt explanations
            to the student's level and present context.
            {self.format_context_for_prompt(context)}
            """

        # Communication style
        style_guide = """
        Communication Style:
        - Be conversational and encouraging
        - Use "we" to work through problems together
        - Ask clarifying questions if the student's request is unclear
        - Offer to show different solution approaches
        - Suggest related practice problems
        - Celebrate progress and correct thinking
        - Gently correct errors with explanations

        When showing mathematical solutions:
        - Use clear formatting (ASCII math or explain in words)
        - Number your steps
        - Explain each step briefly
        - Highlight key insights
        - Show final answer clearly

        Example response structure:
        1. Acknowledge the question/problem
        2. Provide conceptual explanation
        3. Show step-by-step solution (if applicable)
        4. Verify the answer
        5. Offer follow-up practice or related concepts
        """

        # Combina all parts
        full_prompt = "\n\n".join([
            base_prompt,
            level_specific,
            materials_section,
            style_guide
        ])

        return full_prompt

    @staticmethod
    def is_lp_related(message: str) -> bool:
        """
        Check if a message is related to Linear Programming.

        Args:
            message: User message

        Returns:
            True if the message appears LP-related
        """
        lp_keywords = [
            "linear programming", "lp", "simplex", "duality", "constraint",
            "objective function", "feasible", "optimal", "maximize", "minimize",
            "slack variable", "shadow price", "sensitivity", "graphical method",
            "basic variable", "pivot", "tableau", "formulation", "optimization"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in lp_keywords)

    def generate_response(self, user_message: str,
                          conversation_history: List[Dict[str, str]],
                          context: Dict[str, Any]) -> str:
        """
        Generate LP tutor response with preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response
        """

        # Preprocess message
        if not self.validate_message(user_message):
            return "I didn't receive a valid message. Could you please try again?"

        preprocessed_message = self.preprocess_message(user_message)

        # Check if the question is LP-related
        if not self.is_lp_related(preprocessed_message):
            off_topic_response = (
                "I'm specifically trained to help with Linear Programming topics. "
                "Your question seems to be about something else. "
                "\n\nI can help you with:\n"
                "- Formulating LP problems\n"
                "- Solving problems using graphical method or simplex\n"
                "- Understanding duality and sensitivity analysis\n"
                "- Working through LP examples and applications\n"
                "\nWould you like to ask about any of these Linear Programming topics?"
            )
            return off_topic_response

        # Generate response using base class method
        response = super().generate_response(
            preprocessed_message,
            conversation_history,
            context
        )

        final_response = self.postprocess_response(response)
        return final_response

    async def a_generate_response(
            self,
            user_message: str,
            conversation_history: List[Dict[str, str]],
            context: Dict[str, Any]
    ) -> str:
        """
        Async version with preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response
        """
        # Preprocess
        if not self.validate_message(user_message):
            return "I didn't receive a valid message. Could you please try again?"

        preprocessed_message = self.preprocess_message(user_message)

        # Check if LP-related
        if not self.is_lp_related(preprocessed_message):
            off_topic_response = (
                "I'm specifically trained to help with Linear Programming. "
                "Please ask me about LP formulation, simplex method, duality, "
                "or other Linear Programming topics!"
            )
            return off_topic_response

        # Generate async
        response = await super().a_generate_response(
            preprocessed_message,
            conversation_history,
            context
        )

        # Postprocess
        final_response = self.postprocess_response(response)

        return final_response

# Global agent instance
_lp_agent: Optional[LinearProgrammingAgent] = None

def get_linear_programming_agent() -> LinearProgrammingAgent:
    """
    Get or create the global Linear Programming agent instance.

    Returns:
        LinearProgrammingAgent instance
    """
    global _lp_agent

    if _lp_agent is None:
        _lp_agent = LinearProgrammingAgent()

    return _lp_agent