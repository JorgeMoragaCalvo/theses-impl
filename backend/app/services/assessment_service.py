from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import logging
import json

from ..services.llm_service import get_llm_service
from ..services.conversation_service import ConversationService
from ..database import Topic

"""
Assessment Service - Handles personalized assessment generation.
Uses LLM to create tailored exercises based on student context and weaknesses.
"""

logger = logging.getLogger(__name__)


class AssessmentService:
    """
    Service for generating personalized assessments using LLM.
    """

    def __init__(self, db: Session):
        """
        Initialize assessment service.

        Args:
            db: Database session
        """
        self.db = db
        self.llm_service = get_llm_service()
        self.conversation_service = ConversationService(db)

    def generate_personalized_assessment(
        self,
        student_id: int,
        topic: Topic,
        difficulty: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a personalized assessment question tailored to the student's weaknesses.

        Args:
            student_id: Student ID
            topic: Assessment topic (enum)
            difficulty: Difficulty level (beginner, intermediate, advanced)
            conversation_id: Optional conversation ID for context

        Returns:
            Dictionary containing:
                - question: The assessment question/problem
                - correct_answer: Solution to the problem
                - rubric: Grading rubric
                - metadata: Additional generation metadata
        """
        try:
            # Get student context
            student_context = self.conversation_service.get_student_context(
                student_id=student_id,
                topic=topic.value,
                # include_assessment_data=True
            )

            # Get conversation context if conversation_id provided
            conversation_context = None
            if conversation_id:
                conversation_context = self.conversation_service.get_conversation_context(
                    conversation_id=conversation_id,
                    student_id=student_id,
                    topic=topic.value,
                    # include_assessment_data=True
                )

            # Build the assessment generation prompt
            system_prompt = self.build_assessment_prompt(
                student_context=student_context,
                conversation_context=conversation_context,
                topic=topic.value,
                difficulty=difficulty
            )

            # Generate assessment using LLM
            messages = [
                {
                    "role": "user",
                    "content": "Please generate a personalized assessment question following the guidelines provided."
                }
            ]

            response = self.llm_service.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7  # Moderate creativity for varied questions
            )

            # Parse the LLM response
            assessment_data = self.parse_assessment_response(response)

            # Add metadata about personalization
            assessment_data["metadata"] = {
                "difficulty": difficulty,
                "knowledge_level": student_context.get("knowledge_level"),
                "based_on_conversation": conversation_id is not None,
                "knowledge_gaps_addressed": len(student_context.get("knowledge_gaps", [])) > 0
            }

            logger.info(
                f"Generated personalized assessment for student {student_id} on {topic.value} "
                f"(difficulty: {difficulty})"
            )
            return assessment_data

        except Exception as e:
            logger.error(f"Error generating personalized assessment: {str(e)}")
            # Return a fallback assessment
            return self._get_fallback_assessment(topic.value, difficulty)

    @staticmethod
    def build_assessment_prompt(
        student_context: Dict[str, Any],
        conversation_context: Optional[Dict[str, Any]],
        topic: str,
        difficulty: str
    ) -> str:
        """
        Build a comprehensive system prompt for assessment generation.

        Args:
            student_context: Student's knowledge levels, weaknesses, performance
            conversation_context: Recent conversation context (if available)
            topic: Assessment topic
            difficulty: Difficulty level

        Returns:
            System prompt string
        """
        # Extract student information
        knowledge_level = student_context.get("knowledge_level", "beginner")
        knowledge_gaps = student_context.get("knowledge_gaps", [])
        assessment_performance = student_context.get("assessment_performance", {})
        recent_scores = assessment_performance.get("recent_scores", [])

        # Build base prompt
        prompt = f"""You are an expert educational assessment designer for optimization methods and operations research.

        Your task is to generate a personalized assessment question for a student learning about {topic}.
        
        ## Student Profile:
        - Knowledge Level: {knowledge_level} ({student_context.get('knowledge_level_description', '')})
        - Average Score on Past Assessments: {assessment_performance.get('average_score', 'N/A')}
        - Recent Performance: {recent_scores if recent_scores else 'No prior assessments'}
        """

        # Add knowledge gaps if available
        if knowledge_gaps:
            prompt += f"\n## Identified Knowledge Gaps:\n"
            for gap in knowledge_gaps:
                prompt += f"- {gap}\n"
            prompt += "\nPlease design the assessment to target these weak areas.\n"

        # Add conversation context if available
        if conversation_context:
            conversation_extra = conversation_context.get("conversation_extra_data", {})
            strategies_used = conversation_extra.get("strategies_used", [])
            successful_strategies = conversation_extra.get("successful_strategies", {})

            # Get recent topics from the conversation
            recent_messages = conversation_context.get("conversation_history", [])
            if recent_messages:
                recent_topics_summary = "Recent discussion topics: " + "; ".join(
                    [msg.get("content", "")[:100] for msg in recent_messages[-3:] if msg.get("role") == "user"]
                )
                prompt += f"\n## Recent Conversation Context:\n{recent_topics_summary}\n"
                prompt += "Please build on concepts recently discussed in the conversation.\n"

            # Add learning preferences
            if strategies_used:
                most_used = max(set(strategies_used), key=strategies_used.count) if strategies_used else None
                prompt += f"\n## Learning Preferences:\n"
                prompt += f"- Teaching strategies used: {', '.join(set(strategies_used[:5]))}\n"
                if most_used:
                    prompt += f"- Most frequently used approach: {most_used}\n"
                if successful_strategies:
                    best_strategy = max(successful_strategies.items(), key=lambda x: x[1])[0]
                    prompt += f"- Most successful strategy: {best_strategy}\n"
                    prompt += f"Please align the problem presentation with the student's preferred learning style.\n"

        # Add difficulty-specific guidelines
        difficulty_guidelines = {
            "beginner": "Focus on fundamental concepts and basic problem-solving. Include step-by-step guidance hints if needed.",
            "intermediate": "Include moderate complexity with multiple steps. Student should demonstrate understanding of core concepts and their application.",
            "advanced": "Create a challenging problem requiring deep understanding, critical thinking, and potentially multiple solution approaches."
        }
        prompt += f"\n## Difficulty Level: {difficulty}\n{difficulty_guidelines.get(difficulty, '')}\n"

        # Add topic-specific guidelines
        topic_guidelines = {
            "linear_programming": """
            Generate a Linear Programming problem involving:
            - Problem formulation (decision variables, objective function, constraints)
            - Solution method (graphical method for 2 variables, or simplex for more)
            - Interpretation of results
            Ensure the problem is practical and relatable.""", "mathematical_modeling": """
            Generate a Mathematical Modeling problem involving:
            - Translating a real-world scenario into mathematical formulation
            - Identifying decision variables and parameters
            - Formulating objective function and constraints
            - Explaining the reasoning behind the model
            Focus on realistic business or operational scenarios.""",
            "operations_research": """
            Generate an Operations Research problem that may involve:
            - Optimization problem formulation
            - Resource allocation
            - Decision analysis
            - Practical application context""",
            "integer_programming": """
            Generate an Integer Programming problem involving:
            - Discrete decision variables
            - Practical scenarios requiring whole number solutions
            - Formulation and solving techniques""",
            "nonlinear_programming": """
            Generate a Nonlinear Programming problem involving:
            - Nonlinear objective functions or constraints
            - Optimization techniques
            - Practical applications"""
        }
        prompt += f"\n## Topic Guidelines:\n{topic_guidelines.get(topic, 'Generate a relevant optimization problem.')}\n"

        # Output format instructions
        prompt += """
        ## Output Format:
        Please provide your response in the following JSON format:

        ```json
        {
            "question": "The complete problem statement with all necessary information and context",
            "correct_answer": "Detailed step-by-step solution showing all work and reasoning",
            "rubric": "Grading rubric with point allocation: e.g., 'Formulation (3 pts), Solution (3 pts), Interpretation (1 pt)'"
        }
        ```

        ## Important Guidelines:
        1. Make the question clear, specific, and complete
        2. Ensure the problem is solvable with the student's current knowledge level
        3. Target identified weaknesses while building on strengths
        4. Provide a comprehensive solution that could serve as a teaching tool
        5. Create a fair and objective grading rubric (default max score: 7.0 points)
        6. Use realistic, engaging scenarios when possible
        7. IMPORTANT: Respond ONLY with the JSON object, no additional text before or after

        Generate the assessment now.
        """

        return prompt

    def parse_assessment_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse the LLM response to extract question, answer, and rubric.

        Args:
            llm_response: Raw LLM response

        Returns:
            Dictionary with parsed components
        """
        try:
            # Try to extract JSON from the response
            # Remove Markdown code blocks if present
            response_text = llm_response.strip()
            if "```json" in response_text:
                # Extract content between ```json and ```
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract content between ``` and ```
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            # Parse JSON
            parsed = json.loads(response_text)

            return {
                "question": parsed.get("question", ""),
                "correct_answer": parsed.get("correct_answer", ""),
                "rubric": parsed.get("rubric", "")
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            # Fallback: try to extract sections manually
            return self._parse_fallback(llm_response)

    @staticmethod
    def _parse_fallback(llm_response: str) -> Dict[str, Any]:
        """
        Fallback parser when JSON parsing fails.

        Args:
            llm_response: Raw LLM response

        Returns:
            Dictionary with best-effort parsed components
        """
        # Try to identify sections by common markers
        question = ""
        answer = ""
        rubric = ""

        lines = llm_response.split("\n")
        current_section = None

        for line in lines:
            line_lower = line.lower().strip()
            if "question:" in line_lower or line_lower.startswith("question"):
                current_section = "question"
                question = line.split(":", 1)[1].strip() if ":" in line else ""
            elif "answer:" in line_lower or "solution:" in line_lower:
                current_section = "answer"
                answer = line.split(":", 1)[1].strip() if ":" in line else ""
            elif "rubric:" in line_lower or "grading" in line_lower:
                current_section = "rubric"
                rubric = line.split(":", 1)[1].strip() if ":" in line else ""
            elif current_section == "question":
                question += " " + line
            elif current_section == "answer":
                answer += " " + line
            elif current_section == "rubric":
                rubric += " " + line

        return {
            "question": question.strip() if question else llm_response[:500],
            "correct_answer": answer.strip() if answer else "Solution not generated properly.",
            "rubric": rubric.strip() if rubric else "Standard grading rubric applies."
        }

    @staticmethod
    def _get_fallback_assessment(topic: str, difficulty: str) -> Dict[str, Any]:
        """
        Get a fallback assessment when the generation fails.

        Args:
            topic: Assessment topic
            difficulty: Difficulty level

        Returns:
            Basic assessment dictionary
        """
        return {
            "question": f"Practice problem for {topic} at {difficulty} level. (Assessment generation temporarily unavailable)",
            "correct_answer": "Solution will be provided upon submission.",
            "rubric": "Standard grading criteria: Problem understanding (2 pts), Methodology (3 pts), Solution accuracy (2 pts)",
            "metadata": {
                "difficulty": difficulty,
                "is_fallback": True
            }
        }


def get_assessment_service(db: Session) -> AssessmentService:
    """
    Create an assessment service instance.

    Args:
        db: Database session

    Returns:
        AssessmentService instance
    """
    return AssessmentService(db)
