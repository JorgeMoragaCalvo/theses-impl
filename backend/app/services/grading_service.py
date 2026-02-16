import json
import logging
import re

from sqlalchemy.orm import Session

from ..database import Assessment
from ..services.llm_service import get_llm_service
from .llm_response_parser import parse_llm_json_response

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

    def grade_assessment(self, assessment: Assessment, competency_service=None) -> tuple[float, str]:
        """
        Automatically grade an assessment using LLM.

        Args:
            assessment: Assessment object to grade
            competency_service: Optional CompetencyService to update student competencies

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

            # Get concept IDs for this topic to guide the LLM
            available_concepts = None
            if competency_service:
                try:
                    from .competency_service import get_taxonomy_registry
                    registry = get_taxonomy_registry()
                    topic_str = assessment.topic.value if hasattr(assessment.topic, 'value') else str(assessment.topic)
                    concepts = registry.get_concepts_for_topic(topic_str)
                    if concepts:
                        available_concepts = [c["concept_id"] for c in concepts]
                except Exception as e:
                    logger.warning(f"Could not load concept taxonomy: {e}")

            # Build grading prompt
            system_prompt = self.build_grading_prompt(
                question=assessment.question,
                student_answer=assessment.student_answer,
                correct_answer=assessment.correct_answer,
                rubric=assessment.rubric,
                max_score=assessment.max_score,
                topic=assessment.topic.value if hasattr(assessment.topic, 'value') else str(assessment.topic),
                available_concepts=available_concepts,
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
            score, feedback, concepts_tested = self.parse_grading_response(response, assessment.max_score)

            # Update competencies if service provided
            if competency_service and concepts_tested and assessment.student_id:
                try:
                    from .competency_service import get_taxonomy_registry
                    registry = get_taxonomy_registry()
                    valid_concepts = [c for c in concepts_tested if registry.concept_exists(c)]
                    performance_score = score / assessment.max_score if assessment.max_score else 0.0
                    is_correct = performance_score >= 0.6
                    for concept_id in valid_concepts:
                        try:
                            competency_service.update_competency(
                                student_id=assessment.student_id,
                                concept_id=concept_id,
                                is_correct=is_correct,
                                performance_score=performance_score,
                            )
                        except Exception as e:
                            logger.error(f"Error updating competency for {concept_id}: {e}")
                except Exception as e:
                    logger.error(f"Error in competency update pipeline: {e}")

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
        topic: str,
        available_concepts: list[str] | None = None,
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
            available_concepts: Optional list of concept IDs for this topic

        Returns:
            System prompt string
        """
        concepts_section = ""
        concepts_output = ""
        if available_concepts:
            concepts_list = "\n".join(f"            - {c}" for c in available_concepts)
            concepts_section = f"""
            ## Available Concept IDs for This Topic:
{concepts_list}
"""
            concepts_output = ',\n                "concepts_tested": ["concept_id_1", "concept_id_2"]'

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
{concepts_section}
            ## Output Format:
            Please provide your response in the following JSON format:

            ```json
            {{
                "score": <numeric score between 0 and {max_score}>,
                "feedback": "Detailed feedback explaining the grade, highlighting strengths and areas for improvement"{concepts_output}
            }}
            ```

            ## Important:
            - The score MUST be a number between 0 and {max_score}
            - Provide specific, constructive feedback (3-5 sentences minimum)
            - Cite specific parts of the student's answer in your feedback
            - Be encouraging while being honest about mistakes{"" if not available_concepts else """
            - concepts_tested MUST be a list of concept IDs from the Available Concept IDs list above that are relevant to this assessment
            - Only include concepts that are actually tested or demonstrated in the student's answer"""}
            - IMPORTANT: Respond ONLY with the JSON object, no additional text before or after

            Grade the assessment now.
            """
        return prompt

    def parse_grading_response(self, llm_response: str, max_score: float) -> tuple[float, str, list[str]]:
        """
        Parse the LLM grading response to extract score, feedback, and concepts tested.

        Args:
            llm_response: Raw LLM response
            max_score: Maximum possible score for validation

        Returns:
            Tuple of (score, feedback, concepts_tested)
        """
        try:
            # Use the shared parser to get the JSON data
            parsed = parse_llm_json_response(llm_response)

            score = float(parsed.get("score", 0))
            feedback = parsed.get("feedback", "No feedback provided.")

            # Extract concepts_tested if present
            concepts_tested = parsed.get("concepts_tested", [])
            if not isinstance(concepts_tested, list):
                concepts_tested = []
            concepts_tested = [str(c) for c in concepts_tested if isinstance(c, str)]

            # Validate score is within bounds
            score = max(1.0, min(score, max_score))

            return score, feedback, concepts_tested

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse grading response as JSON: {str(e)}")
            # Fallback: try to extract score and feedback manually
            score, feedback = self._parse_fallback(llm_response, max_score)
            return score, feedback, []

    @staticmethod
    def _parse_fallback(llm_response: str, max_score: float) -> tuple[float, str]:
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

        # Extracts score from the response using regex patterns
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
            # Extracts feedback from the response using known markers
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
