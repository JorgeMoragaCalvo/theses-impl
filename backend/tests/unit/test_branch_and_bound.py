"""
Unit tests for BranchAndBoundTool — step-by-step branch-and-bound for IP/MIP.
"""

import json

import pytest
from app.tools.modeling_tools.branch_and_bound import (
    SCIPY_AVAILABLE,
    BranchAndBoundTool,
)
from app.tools.modeling_tools.problem_solver import ProblemSolverTool


def make_json(variables, objective, constraints):
    return json.dumps(
        {
            "variables": variables,
            "objective": objective,
            "constraints": constraints,
        }
    )


@pytest.mark.skipif(not SCIPY_AVAILABLE, reason="scipy not installed")
class TestBranchAndBound:
    def setup_method(self):
        self.tool = BranchAndBoundTool()

    def test_pure_ip_fractional_relaxation(self):
        """max 5x1+4x2 s.t. 6x1+4x2<=24, x1+2x2<=6 (LP gives x2=1.5).

        Integer optimum is z=20 at x1=4, x2=0.
        """
        model = make_json(
            [
                {"name": "x1", "type": "integer", "lower": 0},
                {"name": "x2", "type": "integer", "lower": 0},
            ],
            {"sense": "maximize", "expression": "5*x1 + 4*x2"},
            [
                {"expression": "6*x1 + 4*x2 <= 24", "name": "r1"},
                {"expression": "x1 + 2*x2 <= 6", "name": "r2"},
            ],
        )
        result = self.tool._run(model)

        assert "Óptima" in result
        assert "20.0000" in result
        assert "x1 = 4" in result
        assert "x2 = 0" in result
        # Step-by-step / tree markers
        assert "Árbol de búsqueda" in result
        assert "ramificar" in result
        assert "incumbente" in result

        # Cross-check final optimum against scipy milp via ProblemSolverTool.
        ps = ProblemSolverTool()._run(model)
        assert "20.0000" in ps

    def test_binary_knapsack(self):
        """Binary knapsack: values 60/100/120, weights 10/20/30, capacity 50.

        Optimum: take items 2 and 3 -> z=220.
        """
        result = self.tool._run(
            make_json(
                [
                    {"name": "x1", "type": "binary"},
                    {"name": "x2", "type": "binary"},
                    {"name": "x3", "type": "binary"},
                ],
                {"sense": "maximize", "expression": "60*x1 + 100*x2 + 120*x3"},
                [{"expression": "10*x1 + 20*x2 + 30*x3 <= 50", "name": "cap"}],
            )
        )
        assert "220.0000" in result
        assert "x1 = 0" in result
        assert "x2 = 1" in result
        assert "x3 = 1" in result

    def test_mixed_integer(self):
        """max 2x1+3x2 s.t. x1+x2<=4.5, x1 continuous, x2 integer.

        Optimum: x2=4 (integer), x1=0.5 (continuous), z=13.
        """
        result = self.tool._run(
            make_json(
                [
                    {"name": "x1", "type": "continuous", "lower": 0},
                    {"name": "x2", "type": "integer", "lower": 0},
                ],
                {"sense": "maximize", "expression": "2*x1 + 3*x2"},
                [{"expression": "x1 + x2 <= 4.5", "name": "r1"}],
            )
        )
        assert "13.0000" in result
        assert "x2 = 4" in result

    def test_infeasible(self):
        """x1 integer with lower bound 2 but constraint x1 <= 1 -> infeasible."""
        result = self.tool._run(
            make_json(
                [{"name": "x1", "type": "integer", "lower": 2}],
                {"sense": "maximize", "expression": "x1"},
                [{"expression": "x1 <= 1", "name": "r1"}],
            )
        )
        assert "Infactible" in result

    def test_rejects_continuous_only(self):
        """A model with no integer variables is rejected (use simplex/solver)."""
        result = self.tool._run(
            make_json(
                [
                    {"name": "x1", "type": "continuous", "lower": 0},
                    {"name": "x2", "type": "continuous", "lower": 0},
                ],
                {"sense": "maximize", "expression": "x1 + x2"},
                [{"expression": "x1 + x2 <= 4", "name": "r1"}],
            )
        )
        assert "Error" in result
        assert "enteras" in result

    def test_node_limit_truncation(self, monkeypatch):
        """Hitting the node limit yields a truncation warning."""
        monkeypatch.setattr(BranchAndBoundTool, "MAX_NODES", 1)
        result = self.tool._run(
            make_json(
                [
                    {"name": "x1", "type": "integer", "lower": 0},
                    {"name": "x2", "type": "integer", "lower": 0},
                ],
                {"sense": "maximize", "expression": "5*x1 + 4*x2"},
                [
                    {"expression": "6*x1 + 4*x2 <= 24", "name": "r1"},
                    {"expression": "x1 + 2*x2 <= 6", "name": "r2"},
                ],
            )
        )
        assert "truncada" in result

    def test_invalid_json(self):
        result = self.tool._run("not valid json")
        assert "Error" in result
