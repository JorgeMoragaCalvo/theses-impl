"""
Exercise Assessment Service - Creates assessments from pre-built exercises.
Supports both direct exercise practice and LLM-generated similar problems.
"""

import logging
import os
from typing import Any

from ..models import Topic
from .exercise_manager import ExerciseManager
from .llm_response_parser import parse_llm_json_response
from .llm_service import LLMService, get_llm_service

logger = logging.getLogger(__name__)

# Topic to exercise directory mapping
TOPIC_EXERCISE_PATHS = {
    Topic.MATHEMATICAL_MODELING: "mathematical_modeling/exercises",
    Topic.NONLINEAR_PROGRAMMING: "non_lineal_programming/exercises",
    Topic.LINEAR_PROGRAMMING: "linear_programming/exercises",
    Topic.INTEGER_PROGRAMMING: "integer_programming/exercises",
    Topic.OPERATIONS_RESEARCH: "operations_research/exercises",
}


class ExerciseRegistry:
    """
    Registry managing ExerciseManager instances for all topics.

    Auto-discovers which topics have exercise directories with actual content
    and provides unified access to exercises across all topics.
    """

    def __init__(self, base_path: str):
        """
        Initialize the ExerciseRegistry.

        Args:
            base_path: Base path to the course_materials directory
        """
        self.base_path = base_path
        self._managers: dict[Topic, ExerciseManager] = {}
        self._topic_from_exercise: dict[str, Topic] = {}  # Cache: exercise_id -> topic
        self._discover_topics()

    def _discover_topics(self) -> None:
        """Auto-discover which topics have exercise directories with content."""
        for topic, relative_path in TOPIC_EXERCISE_PATHS.items():
            full_path = os.path.join(self.base_path, relative_path)
            if os.path.exists(full_path):
                manager = ExerciseManager(full_path)
                # Only include it if it has at least one complete exercise
                if manager.get_exercise_count() > 0:
                    self._managers[topic] = manager
                    # Build reverse lookup
                    for ex in manager.list_exercises():
                        self._topic_from_exercise[ex['id']] = topic
                    logger.info(f"Loaded {manager.get_exercise_count()} exercises for {topic.value}")
                else:
                    logger.debug(f"No complete exercises found for {topic.value}")

        logger.info(f"ExerciseRegistry discovered {len(self._managers)} topics with exercises")

    def get_manager(self, topic: Topic) -> ExerciseManager | None:
        """Get an ExerciseManager for a specific topic."""
        return self._managers.get(topic)

    def get_topic_for_exercise(self, exercise_id: str) -> Topic | None:
        """Determine which topic an exercise belongs to."""
        return self._topic_from_exercise.get(exercise_id)

    def list_all_exercises(self) -> list[dict[str, Any]]:
        """List all exercises across all topics."""
        result = []
        for topic, manager in self._managers.items():
            for ex in manager.list_exercises():
                ex_copy = ex.copy()
                ex_copy['topic'] = topic.value
                result.append(ex_copy)
        return result

    def list_exercises_by_topic(self, topic: Topic) -> list[dict[str, Any]]:
        """List exercises for a specific topic."""
        manager = self._managers.get(topic)
        if manager:
            exercises = []
            for ex in manager.list_exercises():
                ex_copy = ex.copy()
                ex_copy['topic'] = topic.value
                exercises.append(ex_copy)
            return exercises
        return []

    def get_topics_with_exercises(self) -> list[Topic]:
        """Return the list of topics that have exercises available."""
        return list(self._managers.keys())

    def exercise_exists(self, exercise_id: str) -> bool:
        """Check if an exercise exists in any topic."""
        return exercise_id in self._topic_from_exercise


# Global instances
_exercise_registry: ExerciseRegistry | None = None
_exercise_manager: ExerciseManager | None = None


def get_exercise_registry() -> ExerciseRegistry:
    """Get or create the global ExerciseRegistry instance."""
    global _exercise_registry
    if _exercise_registry is None:
        base_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "data", "course_materials"
        )
        _exercise_registry = ExerciseRegistry(base_path)
    return _exercise_registry


def get_exercise_manager() -> ExerciseManager:
    """
    Get ExerciseManager for mathematical modeling (backward compatibility).

    For new code, prefer using get_exercise_registry() instead.
    """
    global _exercise_manager
    if _exercise_manager is None:
        registry = get_exercise_registry()
        manager = registry.get_manager(Topic.MATHEMATICAL_MODELING)
        if manager:
            _exercise_manager = manager
        else:
            # Fallback to direct initialization if the registry doesn't have MM
            exercises_path = os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..", "data",
                "course_materials", "mathematical_modeling", "exercises"
            )
            _exercise_manager = ExerciseManager(exercises_path)
            logger.info(f"Initialized ExerciseManager with {_exercise_manager.get_exercise_count()} exercises")
    return _exercise_manager


def get_exercise_assessment_service() -> "ExerciseAssessmentService":
    """Create an ExerciseAssessmentService instance."""
    return ExerciseAssessmentService(
        exercise_manager=get_exercise_manager(),
        llm_service=get_llm_service()
    )


class ExerciseAssessmentService:
    """
    Service for creating assessments from mathematical modeling exercises.

    Supports two modes:
    - practice: Use exercise directly as assessment
    - similar: Generate a similar problem using LLM
    """

    def __init__(self, exercise_manager: ExerciseManager, llm_service: LLMService):
        """
        Initialize the service.

        Args:
            exercise_manager: ExerciseManager instance with loaded exercises
            llm_service: LLM service for generating similar problems
        """
        self.exercise_manager = exercise_manager
        self.llm_service = llm_service

    @staticmethod
    def _sanitize_for_log(value: Any) -> str:
        """
        Sanitize a value for safe inclusion in log messages by removing
        line breaks and carriage returns to prevent log injection.
        """
        text = str(value)

        # Remove CRLF, CR, and LF to avoid creating new log lines
        return text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")

    def create_assessment(
        self,
        exercise_id: str,
        mode: str = "practice"
    ) -> dict[str, Any]:
        """
        Create an assessment from an exercise.

        Args:
            exercise_id: The exercise ID (e.g., "mm_01")
            mode: "practice" for direct exercise, "similar" for LLM-generated variation

        Returns:
            Dictionary with question, correct_answer, rubric, metadata

        Raises:
            ValueError: If exercise is not found or invalid mode
        """
        if not self.exercise_manager.exercise_exists(exercise_id):
            raise ValueError(f"Exercise '{exercise_id}' not found")

        if mode not in ("practice", "similar"):
            raise ValueError(f"Invalid mode '{mode}'. Use 'practice' or 'similar'")

        if mode == "practice":
            return self._create_practice_assessment(exercise_id)
        else:
            return self._generate_similar_assessment(exercise_id)

    def _create_practice_assessment(self, exercise_id: str) -> dict[str, Any]:
        """
        Create assessment directly from exercise.

        Uses an exercise statement as a question and model as correct_answer.
        """
        exercise = self.exercise_manager.get_exercise(exercise_id)

        rubric = self._generate_rubric(exercise.model_type)

        # Sanitize exercise_id before logging to prevent log injection
        safe_exercise_id = exercise_id.replace("\r\n", "").replace("\n", "").replace("\n", "")

        logger.info(f"Created practice assessment from exercise {safe_exercise_id}")

        return {
            "question": exercise.statement,
            "correct_answer": exercise.model,
            "rubric": rubric,
            "metadata": {
                "source": "exercise",
                "exercise_id": exercise_id,
                "exercise_title": exercise.title,
                "model_type": exercise.model_type,
                "mode": "practice",
                "hints_available": len(exercise.hints)
            }
        }

    def _generate_similar_assessment(self, exercise_id: str) -> dict[str, Any]:
        """
        Generate a similar problem using LLM based on the exercise.

        Creates a new problem with different context/numbers but the same model type.
        """
        exercise = self.exercise_manager.get_exercise(exercise_id)

        system_prompt = f"""Eres un experto en modelado matemático y optimización.
Tu tarea es crear un problema SIMILAR pero DIFERENTE al ejercicio de referencia.

EJERCICIO ORIGINAL:
{exercise.statement}

SOLUCIÓN DE REFERENCIA:
{exercise.model}

INSTRUCCIONES:
1. Crea un problema que use el mismo tipo de modelo: {exercise.model_type}
2. Cambia el contexto (industria, productos, situación diferente)
3. Usa números diferentes pero mantén complejidad similar
4. El problema debe ser resoluble con las mismas técnicas
5. Incluye todos los datos necesarios para formular el modelo

FORMATO DE RESPUESTA (JSON):
{{
  "question": "El enunciado completo del nuevo problema con todos los datos",
  "correct_answer": "La formulación matemática completa (variables, objetivo, restricciones, tipo)",
  "rubric": "Criterios de evaluación para calificar la respuesta del estudiante"
}}

Genera SOLO el JSON, sin texto adicional."""

        messages = [
            {"role": "user", "content": "Genera un problema similar siguiendo las instrucciones."}
        ]

        try:
            response = self.llm_service.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7,  # Higher creativity for varied problems
                max_tokens=4000
            )

            # Parse the response
            parsed = parse_llm_json_response(response)

            if not parsed or "question" not in parsed:
                safe_exercise_id = self._sanitize_for_log(exercise_id)
                logger.warning(f"Failed to parse LLM response for similar exercise {safe_exercise_id}")
                # Fallback to practice mode
                return self._create_practice_assessment(exercise_id)

            safe_exercise_id = self._sanitize_for_log(exercise_id)
            logger.info(f"Generated similar assessment from exercise {safe_exercise_id}")

            return {
                "question": parsed.get("question", ""),
                "correct_answer": parsed.get("correct_answer", ""),
                "rubric": parsed.get("rubric", self._generate_rubric(exercise.model_type)),
                "metadata": {
                    "source": "exercise_similar",
                    "exercise_id": exercise_id,
                    "exercise_title": exercise.title,
                    "model_type": exercise.model_type,
                    "mode": "similar",
                    "original_exercise": exercise.title
                }
            }

        except Exception as e:
            logger.error(f"Error generating similar assessment: {e}")
            # Fallback to practice mode
            return self._create_practice_assessment(exercise_id)

    @staticmethod
    def _generate_rubric(model_type: str) -> str:
        """
        Generate a standard rubric for mathematical modeling assessments.

        Args:
            model_type: Type of model (e.g., "PL", "PLI")

        Returns:
            Rubric string
        """
        return f"""Rúbrica de Evaluación para Modelo de {model_type}:

1. **Variables de Decisión (30%)** - 2.1 puntos
   - Identificación correcta de qué se puede controlar
   - Definición clara con unidades apropiadas
   - Notación matemática correcta

2. **Función Objetivo (25%)** - 1.75 puntos
   - Sentido correcto (maximizar/minimizar)
   - Expresión matemática correcta
   - Coeficientes apropiados según el problema

3. **Restricciones (35%)** - 2.45 puntos
   - Todas las restricciones relevantes incluidas
   - Formulación matemática correcta
   - Signos de desigualdad apropiados
   - Restricciones de no negatividad/integralidad

4. **Tipo de Modelo (10%)** - 0.7 puntos
   - Identificación correcta del tipo (LP, IP, MIP, NLP)
   - Justificación si se proporciona

Puntuación máxima: 7.0 puntos"""

    def list_available_exercises(self) -> list[dict[str, Any]]:
        """List all available exercises for assessment."""
        return self.exercise_manager.list_exercises()

    def get_exercise_preview(self, exercise_id: str) -> dict[str, Any] | None:
        """
        Get an exercise preview (statement only, no solution).

        Args:
            exercise_id: The exercise ID

        Returns:
            Dictionary with exercise info or None if not found
        """
        exercise = self.exercise_manager.get_exercise(exercise_id)
        if not exercise:
            return None

        return {
            "id": exercise.id,
            "title": exercise.title,
            "statement": exercise.statement,
            "hints": exercise.hints,
            "model_type": exercise.model_type,
            "hints_count": len(exercise.hints)
        }
