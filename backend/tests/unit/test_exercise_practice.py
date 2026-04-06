"""
Unit tests for ExercisePracticeTool — listing, getting, hinting, and revealing exercises.
"""

import json
from unittest.mock import MagicMock

from app.tools.modeling_tools.exercise_practice import ExercisePracticeTool


def make_tool(
    exercises=None, statement="Problem statement", hints=None, solution="Solution"
):
    """Create an ExercisePracticeTool with mocked ExerciseManager."""
    mgr = MagicMock()
    if exercises is None:
        exercises = [
            {
                "id": "mm_01",
                "title": "Transport",
                "model_type": "LP",
                "difficulty": "easy",
            },
            {
                "id": "mm_02",
                "title": "Knapsack",
                "model_type": "IP",
                "difficulty": None,
            },
        ]
    mgr.list_exercises.return_value = exercises
    mgr.exercise_exists.side_effect = lambda eid: eid in ("mm_01", "mm_02")
    mgr.get_statement.return_value = statement
    mgr.get_hints.return_value = (
        hints if hints is not None else ["Hint 1", "Hint 2", "Hint 3"]
    )
    mgr.get_solution.return_value = solution
    return ExercisePracticeTool(exercise_manager=mgr)


class TestActionList:
    def test_list_exercises(self):
        tool = make_tool()
        result = tool._run(json.dumps({"action": "list"}))
        assert "mm_01" in result
        assert "Transport" in result
        assert "Total: 2" in result

    def test_list_empty(self):
        tool = make_tool(exercises=[])
        result = tool._run(json.dumps({"action": "list"}))
        assert "No hay ejercicios" in result


class TestActionGetExercise:
    def test_get_exercise(self):
        tool = make_tool()
        result = tool._run(
            json.dumps({"action": "get_exercise", "exercise_id": "mm_01"})
        )
        assert "Problem statement" in result
        assert "3 pista(s)" in result

    def test_get_exercise_not_found(self):
        tool = make_tool()
        result = tool._run(
            json.dumps({"action": "get_exercise", "exercise_id": "mm_99"})
        )
        assert "no encontrado" in result

    def test_get_exercise_no_id(self):
        tool = make_tool()
        result = tool._run(json.dumps({"action": "get_exercise"}))
        assert "Se requiere" in result


class TestActionGetHint:
    def test_get_first_hint(self):
        tool = make_tool()
        result = tool._run(
            json.dumps({"action": "get_hint", "exercise_id": "mm_01", "hint_index": 0})
        )
        assert "Hint 1" in result
        assert "Pista 1 de 3" in result
        assert "2 pista(s) más" in result

    def test_get_last_hint(self):
        tool = make_tool()
        result = tool._run(
            json.dumps({"action": "get_hint", "exercise_id": "mm_01", "hint_index": 2})
        )
        assert "Hint 3" in result
        assert "más" not in result

    def test_hint_out_of_range(self):
        tool = make_tool()
        result = tool._run(
            json.dumps({"action": "get_hint", "exercise_id": "mm_01", "hint_index": 10})
        )
        assert "fuera de rango" in result

    def test_hint_no_exercise_id(self):
        tool = make_tool()
        result = tool._run(json.dumps({"action": "get_hint"}))
        assert "Se requiere" in result

    def test_hint_exercise_not_found(self):
        tool = make_tool()
        result = tool._run(json.dumps({"action": "get_hint", "exercise_id": "mm_99"}))
        assert "no encontrado" in result

    def test_hint_no_hints(self):
        tool = make_tool(hints=[])
        result = tool._run(
            json.dumps({"action": "get_hint", "exercise_id": "mm_01", "hint_index": 0})
        )
        assert "no tiene pistas" in result

    def test_hint_invalid_index_type(self):
        tool = make_tool()
        result = tool._run(
            json.dumps(
                {"action": "get_hint", "exercise_id": "mm_01", "hint_index": "abc"}
            )
        )
        assert "entero" in result


class TestActionRevealSolution:
    def test_reveal_solution(self):
        tool = make_tool()
        result = tool._run(
            json.dumps({"action": "reveal_solution", "exercise_id": "mm_01"})
        )
        assert "Solution" in result
        assert "referencia" in result

    def test_reveal_no_solution(self):
        tool = make_tool(solution=None)
        result = tool._run(
            json.dumps({"action": "reveal_solution", "exercise_id": "mm_01"})
        )
        assert "No hay solución" in result

    def test_reveal_no_exercise_id(self):
        tool = make_tool()
        result = tool._run(json.dumps({"action": "reveal_solution"}))
        assert "Se requiere" in result

    def test_reveal_not_found(self):
        tool = make_tool()
        result = tool._run(
            json.dumps({"action": "reveal_solution", "exercise_id": "mm_99"})
        )
        assert "no encontrado" in result


class TestEdgeCases:
    def test_invalid_json(self):
        tool = make_tool()
        result = tool._run("not json")
        assert "Error" in result

    def test_non_dict_input(self):
        tool = make_tool()
        result = tool._run(json.dumps([1, 2]))
        assert "Error" in result

    def test_unknown_action(self):
        tool = make_tool()
        result = tool._run(json.dumps({"action": "delete_everything"}))
        assert "no reconocida" in result
