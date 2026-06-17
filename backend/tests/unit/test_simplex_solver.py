"""
Unit tests for SimplexSolverTool — step-by-step two-phase Simplex.
"""

import json

import pytest
from app.tools.modeling_tools.simplex_solver import (
    NUMPY_AVAILABLE,
    SimplexSolverTool,
)


def make_json(variables, objective, constraints):
    return json.dumps(
        {
            "variables": variables,
            "objective": objective,
            "constraints": constraints,
        }
    )


STD_VARS = [
    {"name": "x1", "lower": 0},
    {"name": "x2", "lower": 0},
]


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not installed")
class TestSimplexStandard:
    def setup_method(self):
        self.tool = SimplexSolverTool()

    def test_standard_max_leq(self):
        """max 3x1+5x2 s.t. x1+2x2<=10, 2x1+x2<=8 -> z=26, x1=2, x2=4."""
        result = self.tool._run(
            make_json(
                STD_VARS,
                {"sense": "maximize", "expression": "3*x1 + 5*x2"},
                [
                    {"expression": "x1 + 2*x2 <= 10", "name": "r1"},
                    {"expression": "2*x1 + x2 <= 8", "name": "r2"},
                ],
            )
        )
        assert "Óptima" in result
        assert "26.0000" in result
        # x1 = 2, x2 = 4
        assert "x1 = 2.0000" in result
        assert "x2 = 4.0000" in result
        # Step-by-step markers
        assert "Iteración" in result
        assert "entrante" in result
        assert "saliente" in result
        assert "Base" in result  # tableau header

    def test_multiple_iterations(self):
        """The standard problem requires more than one pivot."""
        result = self.tool._run(
            make_json(
                STD_VARS,
                {"sense": "maximize", "expression": "3*x1 + 5*x2"},
                [
                    {"expression": "x1 + 2*x2 <= 10", "name": "r1"},
                    {"expression": "2*x1 + x2 <= 8", "name": "r2"},
                ],
            )
        )
        assert "Iteración 1" in result
        assert "Iteración 2" in result


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not installed")
class TestSimplexTwoPhase:
    def setup_method(self):
        self.tool = SimplexSolverTool()

    def test_geq_constraint_runs_phase_one(self):
        """A >= constraint forces an artificial variable and Phase I."""
        result = self.tool._run(
            make_json(
                STD_VARS,
                {"sense": "maximize", "expression": "3*x1 + 5*x2"},
                [
                    {"expression": "x1 + 2*x2 <= 10", "name": "r1"},
                    {"expression": "2*x1 + x2 <= 8", "name": "r2"},
                    {"expression": "x1 + x2 >= 3", "name": "r3"},
                ],
            )
        )
        assert "Fase I" in result
        assert "Fase II" in result
        # Optimum unchanged by the non-binding >= 3 constraint.
        assert "26.0000" in result

    def test_equality_constraint(self):
        """min x1+x2 s.t. x1+x2=5 -> optimum 5 via artificial variable path."""
        result = self.tool._run(
            make_json(
                STD_VARS,
                {"sense": "minimize", "expression": "x1 + x2"},
                [{"expression": "x1 + x2 = 5", "name": "eq1"}],
            )
        )
        assert "Fase I" in result
        assert "Óptima" in result
        assert "5.0000" in result

    def test_minimization_with_geq(self):
        """Classic min cost: min 2x1+3x2 s.t. x1+x2>=4, x1+2x2>=6 -> z=10."""
        result = self.tool._run(
            make_json(
                STD_VARS,
                {"sense": "minimize", "expression": "2*x1 + 3*x2"},
                [
                    {"expression": "x1 + x2 >= 4", "name": "c1"},
                    {"expression": "x1 + 2*x2 >= 6", "name": "c2"},
                ],
            )
        )
        assert "Minimización" in result
        assert "Fase I" in result
        # Optimum at x1=2, x2=2 -> 2*2 + 3*2 = 10
        assert "10.0000" in result


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not installed")
class TestSimplexSpecialCases:
    def setup_method(self):
        self.tool = SimplexSolverTool()

    def test_infeasible(self):
        """Contradictory constraints -> Infactible."""
        result = self.tool._run(
            make_json(
                STD_VARS,
                {"sense": "maximize", "expression": "x1 + x2"},
                [
                    {"expression": "x1 + x2 <= 2", "name": "c1"},
                    {"expression": "x1 + x2 >= 5", "name": "c2"},
                ],
            )
        )
        assert "Infactible" in result

    def test_unbounded(self):
        """max x1 s.t. x1 - x2 <= 1, x>=0 -> No Acotado."""
        result = self.tool._run(
            make_json(
                STD_VARS,
                {"sense": "maximize", "expression": "x1"},
                [{"expression": "x1 - x2 <= 1", "name": "c1"}],
            )
        )
        assert "No Acotado" in result


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not installed")
class TestSimplexTextbookTableau:
    """Verify the step *sequence*, not just the final answer."""

    def setup_method(self):
        self.tool = SimplexSolverTool()

    def test_first_pivot_matches_hand_work(self):
        """
        For max 3x1+5x2 s.t. x1+2x2<=10, 2x1+x2<=8:
        first entering = x2 (cj-zj = -5, most negative),
        first leaving = s1 (ratio 10/2=5 < 8/1=8), pivot element = 2.
        """
        result = self.tool._run(
            make_json(
                STD_VARS,
                {"sense": "maximize", "expression": "3*x1 + 5*x2"},
                [
                    {"expression": "x1 + 2*x2 <= 10", "name": "r1"},
                    {"expression": "2*x1 + x2 <= 8", "name": "r2"},
                ],
            )
        )
        # Find the first iteration block.
        first_iter = result.split("Iteración 2")[0]
        assert "`x2`" in first_iter  # entering
        assert "`s1`" in first_iter  # leaving
        # Pivot element is 2.
        assert "Elemento pivote:** 2" in first_iter


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not installed")
class TestSimplexErrors:
    def setup_method(self):
        self.tool = SimplexSolverTool()

    def test_invalid_json(self):
        assert "Error" in self.tool._run("not valid json")

    def test_no_variables(self):
        result = self.tool._run(
            make_json([], {"sense": "max", "expression": "x"}, [])
        )
        assert "Error" in result

    def test_no_constraints(self):
        result = self.tool._run(
            make_json(STD_VARS, {"sense": "max", "expression": "x1"}, [])
        )
        assert "Error" in result

    def test_no_objective(self):
        result = self.tool._run(
            json.dumps(
                {
                    "variables": STD_VARS,
                    "objective": {},
                    "constraints": [{"expression": "x1 <= 1", "name": "c1"}],
                }
            )
        )
        assert "Error" in result

    def test_too_many_variables(self):
        variables = [{"name": f"x{i}", "lower": 0} for i in range(25)]
        result = self.tool._run(
            make_json(
                variables,
                {"sense": "max", "expression": "x0"},
                [{"expression": "x0 <= 1", "name": "c1"}],
            )
        )
        assert "Demasiadas" in result or "Error" in result
