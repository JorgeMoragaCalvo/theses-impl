"""
Spaced Repetition Review Tool.

LangChain tool that allows agents to start and complete concept reviews
within the chat conversation, closing the SM-2 feedback loop.
"""

import json
import logging
from typing import Any

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class SpacedRepetitionReviewTool(BaseTool):
    """
    Tool for managing spaced repetition reviews during conversation.

    Allows the agent to:
    - start_review: Begin a review session for a due concept
    - complete_review: Record the student's performance (0-5 SM-2 scale)
    """

    name: str = "spaced_repetition_review"
    description: str = """Herramienta para gestionar revisiones de repetición espaciada durante la conversación.

Entrada: JSON con la siguiente estructura:
{
  "action": "start_review" | "complete_review",
  "concept_id": "lp.simplex.method",
  "performance_quality": 4
}

Acciones disponibles:
- start_review: Inicia una sesión de revisión para un concepto pendiente. Requiere concept_id.
- complete_review: Registra el resultado de la revisión tras evaluar la respuesta del estudiante. Requiere concept_id y performance_quality (0-5).

Escala de calidad (performance_quality):
  0 - No recordó nada
  1 - Incorrecto, pero reconoció la respuesta al verla
  2 - Incorrecto, pero la respuesta parecía fácil de recordar
  3 - Correcto con dificultad seria
  4 - Correcto tras hesitación
  5 - Respuesta perfecta

Usa esta herramienta cuando:
1. El estudiante responde a una pregunta de revisión sobre un concepto pendiente
2. Necesitas registrar qué tan bien recordó el concepto

Flujo típico:
1. Haz una pregunta sobre el concepto pendiente
2. El estudiante responde
3. Evalúa la calidad de la respuesta (0-5)
4. Llama a complete_review con concept_id y performance_quality

Retorna: Confirmación con la próxima fecha de revisión programada."""

    model_config = {"arbitrary_types_allowed": True}

    db: Any  # SQLAlchemy Session
    student_id: int

    def _run(self, input_json: str) -> str:
        try:
            params = json.loads(input_json)
        except json.JSONDecodeError as e:
            return self._format_error(f"Error al parsear JSON: {str(e)}")

        if not isinstance(params, dict):
            return self._format_error("La entrada debe ser un objeto JSON")

        action = params.get("action", "").lower()

        if action == "start_review":
            return self._action_start_review(params.get("concept_id"))
        elif action == "complete_review":
            return self._action_complete_review(
                params.get("concept_id"),
                params.get("performance_quality"),
            )
        else:
            return self._format_error(
                f"Acción no reconocida: '{action}'. "
                "Acciones válidas: start_review, complete_review"
            )

    def _action_start_review(self, concept_id: str | None) -> str:
        if not concept_id:
            return self._format_error("Se requiere 'concept_id' para iniciar una revisión")

        from ..database import StudentCompetency
        from ..services.spaced_repetition_service import get_spaced_repetition_service

        competency = self.db.query(StudentCompetency).filter(
            StudentCompetency.student_id == self.student_id,
            StudentCompetency.concept_id == concept_id,
        ).first()

        if not competency:
            return self._format_error(
                f"No se encontró registro de competencia para el concepto '{concept_id}'"
            )

        srs = get_spaced_repetition_service(self.db)
        session = srs.create_review_session(self.student_id, concept_id)

        return json.dumps({
            "status": "ok",
            "review_session_id": session.id,
            "concept_id": concept_id,
            "concept_name": competency.concept_name,
            "current_mastery": round(competency.mastery_score, 3),
            "message": f"Sesión de revisión iniciada para '{competency.concept_name}'",
        })

    def _action_complete_review(
        self, concept_id: str | None, performance_quality: int | None
    ) -> str:
        if not concept_id:
            return self._format_error("Se requiere 'concept_id' para completar una revisión")
        if performance_quality is None:
            return self._format_error("Se requiere 'performance_quality' (0-5)")

        try:
            performance_quality = int(performance_quality)
        except (TypeError, ValueError):
            return self._format_error("'performance_quality' debe ser un entero entre 0 y 5")

        if not 0 <= performance_quality <= 5:
            return self._format_error("'performance_quality' debe estar entre 0 y 5")

        from ..database import ReviewSession, StudentCompetency
        from ..services.spaced_repetition_service import get_spaced_repetition_service

        # Find the most recent incomplete review session for this concept
        review = (
            self.db.query(ReviewSession)
            .filter(
                ReviewSession.student_id == self.student_id,
                ReviewSession.concept_id == concept_id,
                ReviewSession.completed_at.is_(None),
            )
            .order_by(ReviewSession.scheduled_at.desc())
            .first()
        )

        if not review:
            # Auto-start a review session if none exists
            srs = get_spaced_repetition_service(self.db)
            review = srs.create_review_session(self.student_id, concept_id)

        srs = get_spaced_repetition_service(self.db)
        try:
            completed = srs.complete_review(
                review_session_id=review.id,
                performance_quality=performance_quality,
            )
        except ValueError as e:
            return self._format_error(str(e))

        competency = self.db.query(StudentCompetency).filter(
            StudentCompetency.student_id == self.student_id,
            StudentCompetency.concept_id == concept_id,
        ).first()

        next_review = completed.next_review_scheduled
        next_review_str = next_review.strftime("%Y-%m-%d") if next_review else "no programada"

        return json.dumps({
            "status": "ok",
            "concept_id": concept_id,
            "performance_quality": performance_quality,
            "next_review_date": next_review_str,
            "updated_mastery_score": round(competency.mastery_score, 3) if competency else None,
            "updated_mastery_level": competency.mastery_level.value if competency else None,
            "message": (
                f"Revisión completada. Calidad: {performance_quality}/5. "
                f"Próxima revisión: {next_review_str}."
            ),
        })

    @staticmethod
    def _format_error(message: str) -> str:
        return json.dumps({"status": "error", "message": message})

    async def _arun(self, input_json: str) -> str:
        return self._run(input_json)
