from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
import logging
import json
import re

from ..services.llm_service import get_llm_service
from ..database import Assessment

"""
Grading Service - Handles automatic LLM-based grading of student assessments.
"""

logger = logging.getLogger(__name__)


class GradingService:
    """
    Service for automatically grading student assessments using LLM.
    """

    def __init__(self, db: Session):
        """
        Initialize grading service.

        Args:
            db: Database session
        """
        self.db = db
        self.llm_service = get_llm_service()

    def grade_assessment(self, assessment: Assessment) -> Tuple[float, str]:
        """
        Automatically grade an assessment using LLM.

        Args:
            assessment: Assessment object to grade

        Returns:
            Tuple of (score, feedback)
        """
        try:
            # Validate inputs
            if not assessment.student_answer:
                return 1.0, "No answer provided."

            if not assessment.correct_answer or not assessment.rubric:
                logger.warning(f"Assessment {assessment.id} missing correct_answer or rubric")
                return 1.0, "Unable to grade: missing grading materials."

            # Build grading prompt
            system_prompt = self.build_grading_prompt(
                question=assessment.question,
                student_answer=assessment.student_answer,
                correct_answer=assessment.correct_answer,
                rubric=assessment.rubric,
                max_score=assessment.max_score,
                topic=assessment.topic.value if hasattr(assessment.topic, 'value') else str(assessment.topic)
            )

            # Generate grading using LLM
            messages = [
                {
                    "role": "user",
                    "content": "Please grade this student's assessment following the guidelines provided."
                }
            ]

            response = self.llm_service.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.3  # Lower temperature for more consistent grading
            )

            # Parse the LLM response
            score, feedback = self.parse_grading_response(response, assessment.max_score)

            logger.info(
                f"Auto-graded assessment {assessment.id} - Score: {score}/{assessment.max_score}"
            )
            return score, feedback

        except Exception as e:
            logger.error(f"Error auto-grading assessment {assessment.id}: {str(e)}")
            # Return a neutral score with the error message
            return 1.0, f"Unable to auto-grade this assessment. Error: {str(e)}"

    @staticmethod
    def build_grading_prompt(
        question: str,
        student_answer: str,
        correct_answer: str,
        rubric: str,
        max_score: float,
        topic: str
    ) -> str:
        """
        Build a comprehensive system prompt for assessment grading.

        Args:
            question: The assessment question
            student_answer: Student's submitted answer
            correct_answer: Reference correct answer
            rubric: Grading rubric
            max_score: Maximum possible score
            topic: Assessment topic

        Returns:
            System prompt string
        """
        prompt = f"""You are an expert grader for {topic} assessments in operations research and optimization methods.

            Your task is to grade a student's answer fairly and objectively, providing constructive feedback.

            ## Assessment Question:
            {question}

            ## Student's Answer:
            {student_answer}

            ## Reference Solution:
            {correct_answer}

            ## Grading Rubric:
            {rubric}

            ## Maximum Score: {max_score} points

            ## Grading Guidelines:
            1. **Be Fair and Objective**: Grade based on the rubric and the correctness of the approach and solution
            2. **Partial Credit**: Award partial credit for correct methodology even if the final answer is wrong
            3. **Show Your Work**: Explain what the student did correctly and where they made mistakes
            4. **Be Constructive**: Provide specific, actionable feedback that helps the student improve
            5. **Check Understanding**: Evaluate whether the student demonstrates understanding of core concepts
            6. **Minor Errors**: Don't penalize heavily for minor arithmetic errors if the approach is correct
            7. **Alternative Approaches**: Accept valid alternative solution methods if they're correct
            8. **Completeness**: Consider whether the student fully addressed all parts of the question

            ## Output Format:
            Please provide your response in the following JSON format:

            ```json
            {{
                "score": <numeric score between 0 and {max_score}>,
                "feedback": "Detailed feedback explaining the grade, highlighting strengths and areas for improvement"
            }}
            ```

            ## Important:
            - The score MUST be a number between 0 and {max_score}
            - Provide specific, constructive feedback (3-5 sentences minimum)
            - Cite specific parts of the student's answer in your feedback
            - Be encouraging while being honest about mistakes
            - IMPORTANT: Respond ONLY with the JSON object, no additional text before or after

            Grade the assessment now.
            """
        return prompt

    def parse_grading_response(self, llm_response: str, max_score: float) -> Tuple[float, str]:
        """
        Parse the LLM grading response to extract score and feedback.

        Args:
            llm_response: Raw LLM response
            max_score: Maximum possible score for validation

        Returns:
            Tuple of (score, feedback)
        """
        try:
            # Try to extract JSON from the response
            response_text = llm_response.strip()

            # Remove Markdown code blocks if present
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            # Parse JSON
            parsed = json.loads(response_text)

            score = float(parsed.get("score", 0))
            feedback = parsed.get("feedback", "No feedback provided.")

            # Validate score is within bounds
            score = max(1.0, min(score, max_score))

            return score, feedback

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse grading response as JSON: {str(e)}")
            # Fallback: try to extract score and feedback manually
            return self._parse_fallback(llm_response, max_score)

    @staticmethod
    def _parse_fallback(llm_response: str, max_score: float) -> Tuple[float, str]:
        """
        Fallback parser when JSON parsing fails.

        Args:
            llm_response: Raw LLM response
            max_score: Maximum possible score

        Returns:
            Tuple of (score, feedback)
        """
        score = 1.0
        feedback = llm_response

        # Try to find score patterns
        score_patterns = [
            r'score["\s:]+(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*(?:points?|pts?|/\s*' + str(max_score) + ')',
            r'grade["\s:]+(\d+\.?\d*)',
        ]

        for pattern in score_patterns:
            match = re.search(pattern, llm_response, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    score = max(0.0, min(score, max_score))
                    break
                except ValueError:
                    continue

        # Try to extract the feedback section
        feedback_markers = ["feedback:", "evaluation:", "comments:"]
        for marker in feedback_markers:
            if marker in llm_response.lower():
                idx = llm_response.lower().find(marker)
                feedback = llm_response[idx + len(marker):].strip()
                break

        # If no clear feedback, use the whole response
        if not feedback or len(feedback) < 20:
            feedback = llm_response

        # Limit feedback length
        if len(feedback) > 1000:
            feedback = feedback[:1000] + "..."

        return score, feedback

def get_grading_service(db: Session) -> GradingService:
    """
    Create a grading service instance.

    Args:
        db: Database session

    Returns:
        GradingService instance
    """
    return GradingService(db)
