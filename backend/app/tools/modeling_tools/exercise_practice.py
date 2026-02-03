"""
Exercise Practice Tool for Mathematical Modeling.

This tool allows students to practice with mathematical modeling exercises,
providing statements, hints, and solutions.
"""

import json
import logging
from typing import TYPE_CHECKING, Any

from langchain_core.tools import BaseTool


if TYPE_CHECKING:
    from ...services.exercise_manager import ExerciseManager

logger = logging.getLogger(__name__)


class ExercisePracticeTool(BaseTool):
    """
    Tool for practicing mathematical modeling exercises.

    Provides actions to:
    - List available exercises
    - Get exercise statements (without solutions)
    - Get progressive hints
    - Reveal complete solutions
    """

    name: str = "exercise_practice"
    description: str = """Herramienta para practicar ejercicios de modelado matemático.

Entrada: JSON con la siguiente estructura:
{
  "action": "list" | "get_exercise" | "get_hint" | "reveal_solution",
  "exercise_id": "mm_01",
  "hint_index": 0
}

Acciones disponibles:
- list: Muestra todos los ejercicios disponibles (id, título, tipo de modelo)
- get_exercise: Obtiene el enunciado de un ejercicio (sin solución). Requiere exercise_id.
- get_hint: Obtiene una pista específica (0-based index). Requiere exercise_id y hint_index.
- reveal_solution: Muestra la formulación completa del modelo. Requiere exercise_id.

Retorna: El contenido solicitado según la acción."""

    model_config = {"arbitrary_types_allowed": True}

    exercise_manager: Any  # ExerciseManager - using Any to avoid pydantic issues

    def _run(self, input_json: str) -> str:
        """
        Execute the exercise practice action.

        Args:
            input_json: JSON string with action and parameters

        Returns:
            Result of the requested action
        """
        # Parse input
        try:
            params = json.loads(input_json)
        except json.JSONDecodeError as e:
            return self._format_error(f"Error al parsear JSON: {str(e)}")

        if not isinstance(params, dict):
            return self._format_error("La entrada debe ser un objeto JSON")

        action = params.get("action", "").lower()

        if action == "list":
            return self._action_list()
        elif action == "get_exercise":
            return self._action_get_exercise(params.get("exercise_id"))
        elif action == "get_hint":
            return self._action_get_hint(
                params.get("exercise_id"),
                params.get("hint_index", 0)
            )
        elif action == "reveal_solution":
            return self._action_reveal_solution(params.get("exercise_id"))
        else:
            return self._format_error(
                f"Acción no reconocida: '{action}'. "
                "Acciones válidas: list, get_exercise, get_hint, reveal_solution"
            )

    def _action_list(self) -> str:
        """List all available exercises."""
        exercises = self.exercise_manager.list_exercises()

        if not exercises:
            return "No hay ejercicios disponibles."

        result = "**Ejercicios Disponibles**\n\n"
        result += "| ID | Título | Tipo de Modelo |\n"
        result += "|-----|--------|----------------|\n"

        for ex in exercises:
            result += f"| {ex['id']} | {ex['title']} | {ex['model_type']} |\n"

        result += f"\n*Total: {len(exercises)} ejercicios*"
        return result

    def _action_get_exercise(self, exercise_id: str | None) -> str:
        """Get exercise statement."""
        if not exercise_id:
            return self._format_error("Se requiere 'exercise_id' para obtener un ejercicio")

        if not self.exercise_manager.exercise_exists(exercise_id):
            return self._format_error(
                f"Ejercicio '{exercise_id}' no encontrado. "
                f"Usa action='list' para ver los ejercicios disponibles."
            )

        statement = self.exercise_manager.get_statement(exercise_id)
        hints = self.exercise_manager.get_hints(exercise_id)

        result = f"**Ejercicio: {exercise_id}**\n\n"
        result += statement
        result += f"\n\n---\n*Este ejercicio tiene {len(hints)} pista(s) disponible(s). "
        result += "Usa action='get_hint' si necesitas ayuda.*"

        return result

    def _action_get_hint(self, exercise_id: str | None, hint_index: int) -> str:
        """Get a specific hint for an exercise."""
        if not exercise_id:
            return self._format_error("Se requiere 'exercise_id' para obtener una pista")

        if not self.exercise_manager.exercise_exists(exercise_id):
            return self._format_error(f"Ejercicio '{exercise_id}' no encontrado")

        # Validate hint_index type
        try:
            hint_index = int(hint_index)
        except (TypeError, ValueError):
            return self._format_error("'hint_index' debe ser un número entero")

        hints = self.exercise_manager.get_hints(exercise_id)

        if not hints:
            return f"El ejercicio '{exercise_id}' no tiene pistas disponibles."

        if hint_index < 0 or hint_index >= len(hints):
            return self._format_error(
                f"Índice de pista fuera de rango. "
                f"El ejercicio tiene {len(hints)} pista(s) (índices 0 a {len(hints) - 1})"
            )

        hint = hints[hint_index]

        result = f"**Pista {hint_index + 1} de {len(hints)} para {exercise_id}:**\n\n"
        result += f"💡 {hint}"

        if hint_index < len(hints) - 1:
            result += f"\n\n*Hay {len(hints) - hint_index - 1} pista(s) más disponible(s).*"

        return result

    def _action_reveal_solution(self, exercise_id: str | None) -> str:
        """Reveal the complete solution for an exercise."""
        if not exercise_id:
            return self._format_error("Se requiere 'exercise_id' para revelar la solución")

        if not self.exercise_manager.exercise_exists(exercise_id):
            return self._format_error(f"Ejercicio '{exercise_id}' no encontrado")

        solution = self.exercise_manager.get_solution(exercise_id)

        if not solution:
            return f"No hay solución disponible para el ejercicio '{exercise_id}'."

        result = f"**Solución del Ejercicio {exercise_id}**\n\n"
        result += solution
        result += "\n\n---\n*Esta es la formulación de referencia. "
        result += "Compara con tu propia formulación para identificar diferencias.*"

        return result

    @staticmethod
    def _format_error(message: str) -> str:
        """Format an error message."""
        return f"❌ **Error:** {message}"

    async def _arun(self, input_json: str) -> str:
        """Async version - delegates to sync since no async IO is needed."""
        return self._run(input_json)
