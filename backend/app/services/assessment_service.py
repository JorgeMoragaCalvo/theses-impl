import json
import logging
import re
from typing import Any

from sqlalchemy.orm import Session

from ..enums import Topic
from ..services.conversation_service import ConversationService
from ..services.llm_service import get_llm_service
from .llm_response_parser import parse_llm_json_response

"""
Assessment Service - Handles personalized assessment generation.
Uses LLM to create tailored exercises based on student context and weaknesses.
"""

logger = logging.getLogger(__name__)


def _sanitize_for_log(value: Any) -> str:
    return str(value).replace("\r", "").replace("\n", "")


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
        conversation_id: int | None = None,
    ) -> dict[str, Any]:
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
                conversation_context = (
                    self.conversation_service.get_conversation_context(
                        conversation_id=conversation_id,
                        student_id=student_id,
                        topic=topic.value,
                        # include_assessment_data=True
                    )
                )

            # Build the assessment generation prompt
            system_prompt = self.build_assessment_prompt(
                student_context=student_context,
                conversation_context=conversation_context,
                topic=topic.value,
                difficulty=difficulty,
            )

            # Generate assessment using LLM
            messages = [
                {
                    "role": "user",
                    "content": "Please generate a personalized assessment question following the guidelines provided.",
                }
            ]

            response = self.llm_service.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.3,  # Moderate creativity for varied questions
                max_tokens=4000,  # Allow longer responses for complete assessments
            )

            # Parse the LLM response
            assessment_data = self.parse_assessment_response(response)

            # Add metadata about personalization
            assessment_data["metadata"] = {
                "difficulty": difficulty,
                "knowledge_level": student_context.get("knowledge_level"),
                "based_on_conversation": conversation_id is not None,
                "knowledge_gaps_addressed": len(
                    student_context.get("knowledge_gaps", [])
                )
                > 0,
            }

            safe_student_id = _sanitize_for_log(student_id)
            safe_topic = _sanitize_for_log(topic.value)
            safe_difficulty = _sanitize_for_log(difficulty)

            logger.info(
                f"Generated personalized assessment for student {safe_student_id} on {safe_topic} "
                f"(difficulty: {safe_difficulty})"
            )
            return assessment_data

        except Exception as e:
            logger.error(f"Error generating personalized assessment: {str(e)}")
            # Return a fallback assessment
            return self._get_fallback_assessment(topic.value, difficulty)

    @staticmethod
    def build_assessment_prompt(
        student_context: dict[str, Any],
        conversation_context: dict[str, Any] | None,
        topic: str,
        difficulty: str,
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
        prompt = f"""Eres un experto en diseño de evaluaciones educativas para cursos de métodos de optimización e investigación de operaciones.
Tu tarea es generar una pregunta de evaluación personalizada para un estudiante que está aprendiendo sobre {topic}.
IMPORTANTE: Toda la evaluación debe estar escrita en español, incluyendo el enunciado, la solución y la rúbrica.

## Perfil del estudiante:
- Nivel de conocimiento: {knowledge_level} ({student_context.get("knowledge_level_description", "")})
- Promedio en evaluaciones anteriores: {assessment_performance.get("average_score", "N/A")}
- Rendimiento reciente: {recent_scores if recent_scores else "Sin evaluaciones previas"}
"""

        # Add knowledge gaps if available
        if knowledge_gaps:
            prompt += "\n## Brechas de conocimiento identificadas:\n"
            for gap in knowledge_gaps:
                prompt += f"- {gap}\n"
            prompt += "\nPor favor, diseña la evaluación para abordar estas áreas débiles.\n"

        # Add conversation context if available
        if conversation_context:
            conversation_extra = conversation_context.get("conversation_extra_data", {})
            strategies_used = conversation_extra.get("strategies_used", [])
            successful_strategies = conversation_extra.get("successful_strategies", {})

            # Get recent topics from the conversation
            recent_messages = conversation_context.get("conversation_history", [])
            if recent_messages:
                recent_topics_summary = "Temas discutidos recientemente: " + "; ".join(
                    [
                        msg.get("content", "")[:100]
                        for msg in recent_messages[-3:]
                        if msg.get("role") == "user"
                    ]
                )
                prompt += (
                    f"\n## Contexto de conversación reciente:\n{recent_topics_summary}\n"
                )
                prompt += (
                    "Por favor, construye sobre los conceptos discutidos recientemente en la conversación.\n"
                )

            # Add learning preferences
            if strategies_used:
                most_used = (
                    max(set(strategies_used), key=strategies_used.count)
                    if strategies_used
                    else None
                )
                prompt += "\n## Preferencias de aprendizaje:\n"
                prompt += f"- Estrategias de enseñanza utilizadas: {', '.join(set(strategies_used[:5]))}\n"
                if most_used:
                    prompt += f"- Enfoque más utilizado: {most_used}\n"
                if successful_strategies:
                    best_strategy = max(
                        successful_strategies.items(), key=lambda x: x[1]
                    )[0]
                    prompt += f"- Estrategia más exitosa: {best_strategy}\n"
                    prompt += "Por favor, alinea la presentación del problema con el estilo de aprendizaje preferido del estudiante.\n"

        # Add difficulty-specific guidelines
        difficulty_guidelines = {
            "beginner": "Enfócate en conceptos fundamentales y resolución básica de problemas. Incluye pistas de orientación paso a paso si es necesario.",
            "intermediate": "Incluye complejidad moderada con múltiples pasos. El estudiante debe demostrar comprensión de los conceptos centrales y su aplicación.",
            "advanced": "Crea un problema desafiante que requiera comprensión profunda, pensamiento crítico y potencialmente múltiples enfoques de solución.",
        }
        prompt += f"\n## Nivel de dificultad: {difficulty}\n{difficulty_guidelines.get(difficulty, '')}\n"

        # Add topic-specific guidelines
        topic_guidelines = {
            "linear_programming": """
            Genera un problema de Programación Lineal que involucre:
            - Formulación del problema (variables de decisión, función objetivo, restricciones)
            - Método de solución (método gráfico para 2 variables, o simplex para más)
            - Interpretación de resultados
            Asegúrate de que el problema sea práctico y relevante.""",
            "mathematical_modeling": """
            Genera un problema de Modelado Matemático que involucre:
            - Traducir un escenario del mundo real a formulación matemática
            - Identificar variables de decisión y parámetros
            - Formular función objetivo y restricciones
            - Explicar el razonamiento detrás del modelo
            Enfócate en escenarios empresariales u operacionales realistas.""",
            "operations_research": """
            Genera un problema de Investigación de Operaciones que pueda involucrar:
            - Formulación de problemas de optimización
            - Asignación de recursos
            - Análisis de decisiones
            - Contexto de aplicación práctica""",
            "integer_programming": """
            Genera un problema de Programación Entera que involucre:
            - Variables de decisión discretas
            - Escenarios prácticos que requieran soluciones en números enteros
            - Técnicas de formulación y resolución""",
            "nonlinear_programming": """
            Genera un problema de Programación No Lineal que involucre:
            - Funciones objetivo o restricciones no lineales
            - Técnicas de optimización
            - Aplicaciones prácticas""",
        }
        prompt += f"\n## Orientaciones por tema:\n{topic_guidelines.get(topic, 'Genera un problema de optimización relevante.')}\n"

        # Output format instructions
        prompt += """
## Formato de salida:
Proporciona tu respuesta en el siguiente formato JSON:

```json
    {
        "question": "El enunciado completo del problema con toda la información y contexto necesarios",
        "correct_answer": "Solución detallada paso a paso mostrando todo el trabajo y razonamiento",
        "rubric": "Rúbrica de calificación con asignación de puntaje: ej. 'Formulación (3 pts), Solución (3 pts), Interpretación (1 pt)'"
    }
```

## Pautas importantes:
1. El enunciado debe ser claro, específico y completo
2. Asegúrate de que el problema sea resoluble con el nivel de conocimiento actual del estudiante
3. Apunta a las debilidades identificadas mientras construyes sobre las fortalezas
4. Proporciona una solución completa que pueda servir como herramienta de enseñanza
5. Crea una rúbrica de calificación justa y objetiva (puntaje máximo por defecto: 7,0 puntos)
6. Usa escenarios realistas y atractivos cuando sea posible
7. NUNCA uses el símbolo $ para valores monetarios; escribe "pesos", "CLP" o solo el número. Reserva el símbolo $ únicamente para notación LaTeX de fórmulas matemáticas.
8. IMPORTANTE: Responde ÚNICAMENTE con el objeto JSON, sin texto adicional antes ni después

Genera la evaluación ahora.
"""

        return prompt

    def parse_assessment_response(self, llm_response: str) -> dict[str, Any]:
        """
        Parse the LLM response to extract question, answer, and rubric.

        Args:
            llm_response: Raw LLM response

        Returns:
            Dictionary with parsed components
        """
        try:
            # Use the shared parser to get the JSON data
            parsed = parse_llm_json_response(llm_response)

            question = parsed.get("question", "")
            if isinstance(question, dict):
                question = (
                    question.get("problem_statement")
                    or question.get("text")
                    or question.get("question")
                    or question.get("statement")
                    or json.dumps(question)
                )
            return {
                "question": question,
                "correct_answer": parsed.get("correct_answer", ""),
                "rubric": parsed.get("rubric", ""),
            }

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            # Fallback: try to extract sections manually
            return self._parse_fallback(llm_response)

    @staticmethod
    def _parse_fallback(llm_response: str) -> dict[str, Any]:
        """
        Fallback parser when JSON parsing fails.

        Args:
            llm_response: Raw LLM response

        Returns:
            Dictionary with best-effort parsed components
        """
        # First attempt: try to find and parse the outermost JSON object in the
        # original response. parse_llm_json_response may have already stripped a
        # code-block and tried parsing on the truncated text — here we search the
        # full original string, so we pick up the JSON even when backticks inside
        # string values caused an early cut.
        json_start = llm_response.find("{")
        json_end = llm_response.rfind("}")
        if json_start != -1 and json_end > json_start:
            try:
                extracted = json.loads(llm_response[json_start : json_end + 1])
                q = extracted.get("question", "")
                a = extracted.get("correct_answer", "")
                r = extracted.get("rubric", "")
                if q:
                    return {"question": q, "correct_answer": a, "rubric": r}
            except json.JSONDecodeError as exc:
                logger.debug(
                    "Fallback JSON extraction failed in _parse_fallback: %s",
                    _sanitize_for_log(exc),
                )

        # Second attempt: regex extraction — handles literal newlines inside JSON string values
        def _re_extract(text: str, field: str) -> str:
            m = re.search(
                r'"' + re.escape(field) + r'"\s*:\s*"((?:[^"\\]|\\.)*)"',
                text,
                re.DOTALL,
            )
            if not m:
                return ""
            return (
                m.group(1)
                .replace("\\n", "\n")
                .replace("\\t", "\t")
                .replace('\\"', '"')
                .replace("\\\\", "\\")
            )

        q = _re_extract(llm_response, "question")
        if q:
            return {
                "question": q,
                "correct_answer": _re_extract(llm_response, "correct_answer"),
                "rubric": _re_extract(llm_response, "rubric"),
            }

        # Fourth attempt: line-based section extraction
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
            "correct_answer": answer.strip()
            if answer
            else "Solution not generated properly.",
            "rubric": rubric.strip() if rubric else "Standard grading rubric applies.",
        }

    @staticmethod
    def _get_fallback_assessment(topic: str, difficulty: str) -> dict[str, Any]:
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
            "metadata": {"difficulty": difficulty, "is_fallback": True},
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
