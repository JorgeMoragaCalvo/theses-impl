"""
Unit tests for ExerciseValidatorTool — parsing model formulations and comparing components.
"""

import json
from unittest.mock import MagicMock

from app.tools.modeling_tools.exercise_validator import (
    ExerciseValidatorTool,
    ModelComponents,
)


def make_tool(
    exercise_exists=True,
    solution="## Variables\nx1 = units\n## Función objetivo\nmin 3*x1",
):
    """Create an ExerciseValidatorTool with mocked dependencies."""
    mgr = MagicMock()
    mgr.exercise_exists.return_value = exercise_exists
    mgr.get_solution.return_value = solution
    llm = MagicMock()
    llm.generate_response.return_value = "Good formulation."
    return ExerciseValidatorTool(exercise_manager=mgr, llm_service=llm)


class TestParseAndValidateInput:
    def test_invalid_json(self):
        tool = make_tool()
        result = tool._parse_and_validate_input("not json")
        assert isinstance(result, str)
        assert "Error" in result

    def test_non_dict(self):
        tool = make_tool()
        result = tool._parse_and_validate_input(json.dumps([1, 2]))
        assert isinstance(result, str)

    def test_missing_exercise_id(self):
        tool = make_tool()
        result = tool._parse_and_validate_input(
            json.dumps({"student_formulation": "x=1"})
        )
        assert isinstance(result, str)
        assert "exercise_id" in result

    def test_empty_formulation(self):
        tool = make_tool()
        result = tool._parse_and_validate_input(
            json.dumps({"exercise_id": "mm_01", "student_formulation": ""})
        )
        assert isinstance(result, str)
        assert "student_formulation" in result

    def test_exercise_not_found(self):
        tool = make_tool(exercise_exists=False)
        result = tool._parse_and_validate_input(
            json.dumps({"exercise_id": "mm_99", "student_formulation": "x=1"})
        )
        assert isinstance(result, str)
        assert "no encontrado" in result

    def test_no_reference_solution(self):
        tool = make_tool(solution=None)
        result = tool._parse_and_validate_input(
            json.dumps({"exercise_id": "mm_01", "student_formulation": "x=1"})
        )
        assert isinstance(result, str)
        assert "referencia" in result

    def test_valid_input(self):
        tool = make_tool()
        result = tool._parse_and_validate_input(
            json.dumps({"exercise_id": "mm_01", "student_formulation": "x=1"})
        )
        assert isinstance(result, tuple)
        assert result[0] == "mm_01"


class TestParseModelMarkdown:
    def setup_method(self):
        self.tool = make_tool()

    def test_parse_variables(self):
        content = """## Variables de decisión
x1 = cantidad de producto A
x2 = cantidad de producto B

## Función objetivo
max 3*x1 + 5*x2

## Restricciones
x1 + x2 <= 10
x1 >= 0
"""
        comp = self.tool._parse_model_markdown(content)
        assert "x1" in comp.variables
        assert "x2" in comp.variables
        assert comp.objective_sense == "max"
        assert len(comp.constraints) >= 2

    def test_parse_minimize(self):
        content = """## Variables
c = costo

## Función objetivo
min c + 10
"""
        comp = self.tool._parse_model_markdown(content)
        assert comp.objective_sense == "min"

    def test_parse_model_type(self):
        content = """## Variables
x1 = units

## Función objetivo
max x1

## Restricciones
x1 <= 5

## Tipo de modelo
Programación Lineal
"""
        comp = self.tool._parse_model_markdown(content)
        assert "Lineal" in comp.model_type

    def test_empty_content(self):
        comp = self.tool._parse_model_markdown("")
        assert comp.variables == []
        assert comp.objective_sense == ""


class TestExtractVariables:
    def test_basic(self):
        section = "x1 = units produced\nx2 = hours worked"
        result = ExerciseValidatorTool._extract_variables(section)
        assert "x1" in result
        assert "x2" in result

    def test_no_variables(self):
        result = ExerciseValidatorTool._extract_variables("no variables here")
        assert result == []

    def test_no_duplicates(self):
        section = "x1 = units\nx1 = repeated"
        result = ExerciseValidatorTool._extract_variables(section)
        assert result.count("x1") == 1


class TestExtractConstraints:
    def test_basic(self):
        section = "x1 + x2 <= 10\nx1 >= 0\n"
        result = ExerciseValidatorTool._extract_constraints(section)
        assert len(result) == 2

    def test_skips_headers(self):
        section = "**Capacity:**\nx1 <= 5\n"
        result = ExerciseValidatorTool._extract_constraints(section)
        assert len(result) == 1

    def test_unicode_operators(self):
        section = "x₁ + x₂ ≤ 10\nx₁ ≥ 0"
        result = ExerciseValidatorTool._extract_constraints(section)
        assert len(result) == 2


class TestCompareComponents:
    def setup_method(self):
        self.tool = make_tool()

    def test_matching_components(self):
        ref = ModelComponents(
            variables=["x1", "x2"],
            objective_sense="max",
            objective_expression="max 3*x1 + 5*x2",
            constraints=["x1 + x2 <= 10", "x1 >= 0"],
            model_type="Programación Lineal",
        )
        student = ModelComponents(
            variables=["x1", "x2"],
            objective_sense="max",
            objective_expression="max 3*x1 + 5*x2",
            constraints=["x1 + x2 <= 10", "x1 >= 0"],
            model_type="Programación Lineal",
        )
        feedback = self.tool._compare_components(ref, student)
        assert feedback["variables"]["count_match"] is True
        assert feedback["objective"]["sense_match"] is True
        assert feedback["model_type"]["type_match"] is True

    def test_mismatched_sense(self):
        ref = ModelComponents(objective_sense="max")
        student = ModelComponents(objective_sense="min")
        feedback = self.tool._compare_components(ref, student)
        assert feedback["objective"]["sense_match"] is False

    def test_missing_variables(self):
        ref = ModelComponents(variables=["x1", "x2", "x3"])
        student = ModelComponents(variables=["x1"])
        feedback = self.tool._compare_components(ref, student)
        assert feedback["variables"]["count_match"] is False

    def test_model_type_match_ip(self):
        ref = ModelComponents(model_type="Programación Entera")
        student = ModelComponents(model_type="Integer Programming")
        result = ExerciseValidatorTool._compare_model_type(ref, student)
        assert result["type_match"] is True

    def test_model_type_mismatch(self):
        ref = ModelComponents(model_type="Programación Lineal")
        student = ModelComponents(model_type="Programación Entera")
        result = ExerciseValidatorTool._compare_model_type(ref, student)
        assert result["type_match"] is False


class TestFormatCombinedFeedback:
    def test_complete_feedback(self):
        structured = {
            "variables": {
                "has_variables": True,
                "count_match": True,
                "student_count": 2,
                "reference_count": 2,
            },
            "objective": {
                "has_objective": True,
                "sense_match": True,
                "student_sense": "max",
                "reference_sense": "max",
            },
            "constraints": {
                "has_constraints": True,
                "student_count": 3,
                "reference_count": 3,
            },
            "model_type": {"has_type": True, "type_match": True, "student_type": "LP"},
        }
        result = ExerciseValidatorTool._format_combined_feedback(
            "mm_01", structured, "Great work!"
        )
        assert "mm_01" in result
        assert "Great work!" in result
        assert "Variables" in result

    def test_missing_components(self):
        structured = {
            "variables": {
                "has_variables": False,
                "count_match": False,
                "student_count": 0,
                "reference_count": 2,
            },
            "objective": {
                "has_objective": False,
                "sense_match": False,
                "student_sense": "",
                "reference_sense": "max",
            },
            "constraints": {
                "has_constraints": False,
                "student_count": 0,
                "reference_count": 3,
            },
            "model_type": {"has_type": False, "type_match": False, "student_type": ""},
        }
        result = ExerciseValidatorTool._format_combined_feedback(
            "mm_01", structured, "Needs work"
        )
        assert "No se identificaron variables" in result
        assert "No se identificó función objetivo" in result


class TestRun:
    def test_full_validation(self):
        tool = make_tool(
            solution="## Variables de decisión\nx1 = units\n## Función objetivo\nmax x1\n## Restricciones\nx1 <= 10"
        )
        input_json = json.dumps(
            {
                "exercise_id": "mm_01",
                "student_formulation": "## Variables\nx1 = units\n## Función objetivo\nmax x1\n## Restricciones\nx1 <= 10",
            }
        )
        result = tool._run(input_json)
        assert "mm_01" in result
        assert "Variables" in result

    def test_semantic_feedback_error_handled(self):
        tool = make_tool(
            solution="## Variables\nx1 = a\n## Función objetivo\nmax x1\n## Restricciones\nx1 <= 5"
        )
        tool.llm_service.generate_response.side_effect = Exception("LLM down")
        input_json = json.dumps(
            {
                "exercise_id": "mm_01",
                "student_formulation": "## Variables\nx1 = a\n## Función objetivo\nmax x1\n## Restricciones\nx1 <= 5",
            }
        )
        result = tool._run(input_json)
        assert "No se pudo obtener feedback semántico" in result
