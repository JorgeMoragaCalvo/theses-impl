"""
Exercise Validator Tool for Mathematical Modeling.

This tool validates student formulations against reference solutions,
providing detailed pedagogical feedback using both structured parsing
and LLM-based semantic comparison.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from langchain_core.tools import BaseTool

# if TYPE_CHECKING:
#     from ...services.exercise_manager import ExerciseManager
#     from ...services.llm_service import LLMService

logger = logging.getLogger(__name__)


@dataclass
class ModelComponents:
    """Parsed components of a mathematical model."""
    variables: list[str] = field(default_factory=list)
    objective_sense: str = ""  # "min" or "max"
    objective_expression: str = ""
    constraints: list[str] = field(default_factory=list)
    model_type: str = ""
    raw_sections: dict[str, str] = field(default_factory=dict)


class ExerciseValidatorTool(BaseTool):
    """
    Tool for validating student formulations against reference solutions.

    Uses both structured parsing and LLM-based semantic comparison to provide
    detailed, pedagogical feedback on mathematical model formulations.
    """

    name: str = "exercise_validator"
    description: str = """Valida la formulación de un estudiante contra la solución de referencia.

Entrada: JSON con la siguiente estructura:
{
  "exercise_id": "mm_01",
  "student_formulation": "Variables: x1 = ...\nObjetivo: min ...\nRestricciones: ..."
}

Analiza:
- Variables de decisión (correctas/faltantes/extras)
- Función objetivo (sentido, componentes)
- Restricciones (cobertura, corrección)
- Identificación del tipo de modelo

Retorna: Feedback pedagógico detallado sobre la formulación."""

    model_config = {"arbitrary_types_allowed": True}

    exercise_manager: Any  # ExerciseManager
    llm_service: Any  # LLMService

    def _run(self, input_json: str) -> str:
        """
        Validate a student's formulation against the reference solution.

        Args:
            input_json: JSON string with exercise_id and student_formulation

        Returns:
            Detailed validation feedback
        """
        # Parse input
        try:
            params = json.loads(input_json)
        except json.JSONDecodeError as e:
            return self._format_error(f"Error al parsear JSON: {str(e)}")

        if not isinstance(params, dict):
            return self._format_error("La entrada debe ser un objeto JSON")

        exercise_id = params.get("exercise_id")
        student_formulation = params.get("student_formulation", "")

        # Validate inputs
        if not exercise_id:
            return self._format_error("Se requiere 'exercise_id'")

        if not student_formulation or not student_formulation.strip():
            return self._format_error("Se requiere 'student_formulation' con contenido")

        if not self.exercise_manager.exercise_exists(exercise_id):
            return self._format_error(
                f"Ejercicio '{exercise_id}' no encontrado. "
                f"Usa la herramienta exercise_practice con action='list' para ver los disponibles."
            )

        # Get reference solution
        reference = self.exercise_manager.get_solution(exercise_id)
        if not reference:
            return self._format_error(f"No hay solución de referencia para '{exercise_id}'")

        # Perform validation
        return self._validate(exercise_id, student_formulation, reference)

    def _validate(
        self, exercise_id: str, student_formulation: str, reference: str
    ) -> str:
        """
        Perform full validation of student formulation.

        Args:
            exercise_id: The exercise identifier
            student_formulation: Student's model formulation
            reference: Reference solution

        Returns:
            Formatted validation feedback
        """
        # 1. Structured parsing and comparison
        ref_components = self._parse_model_markdown(reference)
        student_components = self._parse_model_markdown(student_formulation)
        structured_feedback = self._compare_components(ref_components, student_components)

        # 2. LLM semantic comparison for nuanced feedback
        semantic_feedback = self._get_semantic_feedback(
            exercise_id, student_formulation, reference
        )

        # 3. Combine feedback
        return self._format_combined_feedback(
            exercise_id, structured_feedback, semantic_feedback
        )

    def _parse_model_markdown(self, content: str) -> ModelComponents:
        """
        Parse a model formulation from markdown content.

        Extracts:
        - Variables from "Variables de decisión" section
        - Objective from "Función objetivo" section
        - Constraints from "Restricciones" section
        - Model type from "Tipo de modelo" section
        """
        components = ModelComponents()

        # Parse variables section
        var_match = re.search(
            r"(?:##?\s*)?Variables?\s*(?:de decisión)?\s*\n+(.*?)(?=\n##|\n#|\Z)",
            content, re.IGNORECASE | re.DOTALL
        )
        if var_match:
            var_section = var_match.group(1).strip()
            components.raw_sections["variables"] = var_section
            # Extract variable definitions
            components.variables = self._extract_variables(var_section)

        # Parse objective section
        obj_match = re.search(
            r"(?:##?\s*)?Función objetivo\s*\n+(.*?)(?=\n##|\n#|\Z)",
            content, re.IGNORECASE | re.DOTALL
        )
        if obj_match:
            obj_section = obj_match.group(1).strip()
            components.raw_sections["objective"] = obj_section
            # Determine sense (min/max)
            if re.search(r"\bmin\b", obj_section, re.IGNORECASE):
                components.objective_sense = "min"
            elif re.search(r"\bmax\b", obj_section, re.IGNORECASE):
                components.objective_sense = "max"
            components.objective_expression = obj_section

        # Parse constraints section
        const_match = re.search(
            r"(?:##?\s*)?Restricciones?\s*\n+(.*?)(?=\n##\s*Tipo|\Z)",
            content, re.IGNORECASE | re.DOTALL
        )
        if const_match:
            const_section = const_match.group(1).strip()
            components.raw_sections["constraints"] = const_section
            components.constraints = self._extract_constraints(const_section)

        # Parse model type
        type_match = re.search(
            r"(?:##?\s*)?Tipo de modelo\s*\n+(.*?)(?=\n##|\Z)",
            content, re.IGNORECASE | re.DOTALL
        )
        if type_match:
            type_section = type_match.group(1).strip()
            # Get the first non-empty line
            for line in type_section.split("\n"):
                line = line.strip()
                if line:
                    components.model_type = line
                    break

        return components

    @staticmethod
    def _extract_variables(section: str) -> list[str]:
        """Extract variable definitions from a variables section."""
        variables = []
        # Match patterns like "x_i = ...", "x1 = ...", "x₁ = ..."
        pattern = r"([a-zA-Z_][a-zA-Z0-9_ᵢⱼₖ₁₂₃₄₅₆₇₈₉₀]*)\s*="
        for match in re.finditer(pattern, section):
            var = match.group(1)
            if var not in variables:
                variables.append(var)
        return variables

    @staticmethod
    def _extract_constraints(section: str) -> list[str]:
        """Extract individual constraints from a constraints section."""
        constraints = []
        # Split by constraint markers (bold headers, numbered items, etc.)
        # Look for lines containing constraint operators
        for line in section.split("\n"):
            line = line.strip()
            # Skip headers and empty lines
            if line.startswith("**") and line.endswith(":**"):
                continue
            if not line or line.startswith("#"):
                continue
            # Check if a line contains a constraint operator
            if re.search(r"[≤≥=<>]", line) or re.search(r"<=|>=", line):
                constraints.append(line)
        return constraints

    def _compare_components(
        self, reference: ModelComponents, student: ModelComponents
    ) -> dict[str, Any]:
        """
        Compare student components against reference.

        Returns a dictionary with comparison results for each component.
        """
        feedback = {
            "variables": self._compare_variables(reference, student),
            "objective": self._compare_objective(reference, student),
            "constraints": self._compare_constraints(reference, student),
            "model_type": self._compare_model_type(reference, student),
        }
        return feedback

    @staticmethod
    def _compare_variables(ref: ModelComponents, student: ModelComponents) -> dict[str, Any]:
        """Compare variable definitions."""
        ref_var_count = len(ref.variables)
        student_var_count = len(student.variables)

        return {
            "reference_count": ref_var_count,
            "student_count": student_var_count,
            "student_variables": student.variables,
            "has_variables": student_var_count > 0,
            "count_match": ref_var_count == student_var_count,
        }

    @staticmethod
    def _compare_objective(ref: ModelComponents, student: ModelComponents) -> dict[str, Any]:
        """Compare objective functions."""
        sense_match = (
            ref.objective_sense.lower() == student.objective_sense.lower()
            if ref.objective_sense and student.objective_sense
            else False
        )

        return {
            "reference_sense": ref.objective_sense,
            "student_sense": student.objective_sense,
            "sense_match": sense_match,
            "has_objective": bool(student.objective_expression),
        }

    @staticmethod
    def _compare_constraints(ref: ModelComponents, student: ModelComponents) -> dict[str, Any]:
        """Compare constraints."""
        return {
            "reference_count": len(ref.constraints),
            "student_count": len(student.constraints),
            "has_constraints": len(student.constraints) > 0,
        }

    @staticmethod
    def _compare_model_type(ref: ModelComponents, student: ModelComponents) -> dict[str, Any]:
        """Compare model type identification."""
        ref_type = ref.model_type.lower()
        student_type = student.model_type.lower()

        # Check for key type indicators
        is_lp = any(t in ref_type for t in ["lineal", "linear", "pl"])
        is_ip = any(t in ref_type for t in ["entera", "integer", "pli", "entero"])
        is_binary = any(t in ref_type for t in ["binaria", "binary", "0-1"])

        student_is_lp = any(t in student_type for t in ["lineal", "linear", "pl"])
        student_is_ip = any(t in student_type for t in ["entera", "integer", "pli", "entero"])
        student_is_binary = any(t in student_type for t in ["binaria", "binary", "0-1"])

        type_match = (
            (is_lp == student_is_lp) and
            (is_ip == student_is_ip) and
            (is_binary == student_is_binary)
        )

        return {
            "reference_type": ref.model_type,
            "student_type": student.model_type,
            "type_match": type_match,
            "has_type": bool(student.model_type),
        }

    def _get_semantic_feedback(
        self, exercise_id: str, student_formulation: str, reference: str
    ) -> str:
        """
        Use LLM to provide semantic comparison and nuanced feedback.

        Args:
            exercise_id: The exercise identifier
            student_formulation: Student's formulation
            reference: Reference solution

        Returns:
            LLM-generated feedback string
        """
        prompt = f"""Eres un tutor experto en modelado matemático. Compara la formulación del estudiante con la solución de referencia para el ejercicio {exercise_id}.

SOLUCIÓN DE REFERENCIA:
{reference}

FORMULACIÓN DEL ESTUDIANTE:
{student_formulation}

Analiza y proporciona feedback pedagógico constructivo sobre:
1. ¿Las variables de decisión capturan correctamente lo que se puede controlar en el problema? (pueden tener notación diferente pero ser equivalentes)
2. ¿La función objetivo es matemáticamente equivalente a la referencia?
3. ¿Las restricciones cubren todos los requisitos del problema? ¿Falta alguna restricción importante?
4. ¿El estudiante identificó correctamente el tipo de modelo?
5. ¿Hay errores conceptuales o de formulación que debería corregir?

Responde de forma constructiva y pedagógica, reconociendo lo que está bien y guiando sobre lo que puede mejorar. No des la solución directamente, sino orienta al estudiante."""

        try:
            response = self.llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="Eres un tutor experto en optimización y modelado matemático. Tu objetivo es ayudar al estudiante a mejorar su formulación de manera constructiva.",
                temperature=0.3,  # Lower temperature for more consistent feedback
                max_tokens=1000
            )
            return response
        except Exception as e:
            logger.error(f"Error getting semantic feedback: {e}")
            return "No se pudo obtener feedback semántico adicional."

    @staticmethod
    def _format_combined_feedback(
        exercise_id: str,
        structured: dict[str, Any],
        semantic: str
    ) -> str:
        """Format the combined validation feedback."""
        result = f"**Validación de Formulación - Ejercicio {exercise_id}**\n\n"

        # Structured feedback summary
        result += "## Análisis Estructural\n\n"

        # Variables
        var_info = structured["variables"]
        if var_info["has_variables"]:
            count_status = "✅" if var_info["count_match"] else "⚠️"
            result += f"{count_status} **Variables:** {var_info['student_count']} identificadas "
            result += f"(referencia: {var_info['reference_count']})\n"
        else:
            result += "❌ **Variables:** No se identificaron variables de decisión\n"

        # Objective
        obj_info = structured["objective"]
        if obj_info["has_objective"]:
            sense_status = "✅" if obj_info["sense_match"] else "⚠️"
            result += f"{sense_status} **Objetivo:** "
            if obj_info["student_sense"]:
                result += f"{obj_info['student_sense'].upper()} "
            result += f"(referencia: {obj_info['reference_sense'].upper()})\n"
        else:
            result += "❌ **Objetivo:** No se identificó función objetivo\n"

        # Constraints
        const_info = structured["constraints"]
        if const_info["has_constraints"]:
            result += f"📋 **Restricciones:** {const_info['student_count']} identificadas "
            result += f"(referencia tiene ~{const_info['reference_count']})\n"
        else:
            result += "❌ **Restricciones:** No se identificaron restricciones\n"

        # Model type
        type_info = structured["model_type"]
        if type_info["has_type"]:
            type_status = "✅" if type_info["type_match"] else "⚠️"
            result += f"{type_status} **Tipo de modelo:** {type_info['student_type']}\n"
        else:
            result += "⚠️ **Tipo de modelo:** No especificado\n"

        # Semantic feedback
        result += "\n## Análisis Detallado\n\n"
        result += semantic

        return result

    @staticmethod
    def _format_error(message: str) -> str:
        """Format an error message."""
        return f"❌ **Error:** {message}"

    async def _arun(self, input_json: str) -> str:
        """Async version of the validation."""
        # Parse input synchronously
        try:
            params = json.loads(input_json)
        except json.JSONDecodeError as e:
            return self._format_error(f"Error al parsear JSON: {str(e)}")

        if not isinstance(params, dict):
            return self._format_error("La entrada debe ser un objeto JSON")

        exercise_id = params.get("exercise_id")
        student_formulation = params.get("student_formulation", "")

        if not exercise_id:
            return self._format_error("Se requiere 'exercise_id'")

        if not student_formulation or not student_formulation.strip():
            return self._format_error("Se requiere 'student_formulation' con contenido")

        if not self.exercise_manager.exercise_exists(exercise_id):
            return self._format_error(f"Ejercicio '{exercise_id}' no encontrado")

        reference = self.exercise_manager.get_solution(exercise_id)
        if not reference:
            return self._format_error(f"No hay solución de referencia para '{exercise_id}'")

        # Structured parsing (sync)
        ref_components = self._parse_model_markdown(reference)
        student_components = self._parse_model_markdown(student_formulation)
        structured_feedback = self._compare_components(ref_components, student_components)

        # Async semantic feedback
        semantic_feedback = await self._get_semantic_feedback_async(
            exercise_id, student_formulation, reference
        )

        return self._format_combined_feedback(
            exercise_id, structured_feedback, semantic_feedback
        )

    async def _get_semantic_feedback_async(
        self, exercise_id: str, student_formulation: str, reference: str
    ) -> str:
        """Async version of semantic feedback."""
        prompt = f"""Eres un tutor experto en modelado matemático. Compara la formulación del estudiante con la solución de referencia para el ejercicio {exercise_id}.

SOLUCIÓN DE REFERENCIA:
{reference}

FORMULACIÓN DEL ESTUDIANTE:
{student_formulation}

Analiza y proporciona feedback pedagógico constructivo sobre:
1. ¿Las variables de decisión capturan correctamente lo que se puede controlar en el problema?
2. ¿La función objetivo es matemáticamente equivalente a la referencia?
3. ¿Las restricciones cubren todos los requisitos del problema?
4. ¿El estudiante identificó correctamente el tipo de modelo?
5. ¿Hay errores conceptuales o de formulación?

Responde de forma constructiva, reconociendo lo que está bien y guiando sobre mejoras."""

        try:
            response = await self.llm_service.a_generate_response(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="Eres un tutor experto en optimización y modelado matemático.",
                temperature=0.3,
                max_tokens=1000
            )
            return response
        except Exception as e:
            logger.error(f"Error getting async semantic feedback: {e}")
            return "No se pudo obtener feedback semántico adicional."
