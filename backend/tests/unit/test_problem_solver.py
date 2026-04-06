"""
Unit tests for ProblemSolverTool — LP/IP solving via scipy.
"""

import json

import pytest
from app.tools.modeling_tools.problem_solver import SCIPY_AVAILABLE, ProblemSolverTool


def make_lp_json(**overrides):
    """Standard feasible LP: max 3x1+5x2 s.t. x1+2x2<=10, 2x1+x2<=8, x>=0."""
    model = {
        "variables": [
            {"name": "x1", "type": "continuous", "lower": 0},
            {"name": "x2", "type": "continuous", "lower": 0},
        ],
        "objective": {"sense": "maximize", "expression": "3*x1 + 5*x2"},
        "constraints": [
            {"expression": "x1 + 2*x2 <= 10", "name": "r1"},
            {"expression": "2*x1 + x2 <= 8", "name": "r2"},
        ],
    }
    model.update(overrides)
    return json.dumps(model)


@pytest.mark.skipif(not SCIPY_AVAILABLE, reason="scipy not installed")
class TestProblemSolverLP:
    def setup_method(self):
        self.tool = ProblemSolverTool()

    def test_solve_basic_lp(self):
        result = self.tool._run(make_lp_json())
        assert "Óptima" in result or "Optimal" in result
        assert "x1" in result
        assert "x2" in result

    def test_minimization(self):
        result = self.tool._run(
            make_lp_json(
                objective={"sense": "minimize", "expression": "3*x1 + 5*x2"},
                constraints=[
                    {"expression": "x1 + x2 >= 4", "name": "demand"},
                ],
            )
        )
        assert "Minimización" in result

    def test_equality_constraint(self):
        result = self.tool._run(
            json.dumps(
                {
                    "variables": [
                        {"name": "x1", "type": "continuous", "lower": 0},
                        {"name": "x2", "type": "continuous", "lower": 0},
                    ],
                    "objective": {"sense": "min", "expression": "x1 + x2"},
                    "constraints": [
                        {"expression": "x1 + x2 = 5", "name": "eq1"},
                    ],
                }
            )
        )
        assert "Óptima" in result


@pytest.mark.skipif(not SCIPY_AVAILABLE, reason="scipy not installed")
class TestProblemSolverIP:
    def setup_method(self):
        self.tool = ProblemSolverTool()

    def test_solve_ip(self):
        model = json.dumps(
            {
                "variables": [
                    {"name": "x1", "type": "integer", "lower": 0, "upper": 5},
                    {"name": "x2", "type": "integer", "lower": 0, "upper": 5},
                ],
                "objective": {"sense": "maximize", "expression": "3*x1 + 5*x2"},
                "constraints": [
                    {"expression": "x1 + 2*x2 <= 10", "name": "r1"},
                ],
            }
        )
        result = self.tool._run(model)
        assert "Óptima" in result

    def test_binary_variables(self):
        model = json.dumps(
            {
                "variables": [
                    {"name": "y1", "type": "binary"},
                    {"name": "y2", "type": "binary"},
                ],
                "objective": {"sense": "maximize", "expression": "3*y1 + 5*y2"},
                "constraints": [
                    {"expression": "y1 + y2 <= 1", "name": "choose_one"},
                ],
            }
        )
        result = self.tool._run(model)
        assert "Óptima" in result


@pytest.mark.skipif(not SCIPY_AVAILABLE, reason="scipy not installed")
class TestProblemSolverErrors:
    def setup_method(self):
        self.tool = ProblemSolverTool()

    def test_invalid_json(self):
        result = self.tool._run("not valid json")
        assert "Error" in result

    def test_no_variables(self):
        result = self.tool._run(
            json.dumps(
                {
                    "variables": [],
                    "objective": {"sense": "max", "expression": "x"},
                    "constraints": [],
                }
            )
        )
        assert "Error" in result

    def test_no_objective(self):
        result = self.tool._run(
            json.dumps(
                {
                    "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                    "objective": {},
                    "constraints": [],
                }
            )
        )
        assert "Error" in result

    def test_too_many_variables(self):
        variables = [
            {"name": f"x{i}", "type": "continuous", "lower": 0} for i in range(25)
        ]
        result = self.tool._run(
            json.dumps(
                {
                    "variables": variables,
                    "objective": {"sense": "max", "expression": "x0"},
                    "constraints": [],
                }
            )
        )
        assert "Demasiadas" in result or "Error" in result

    def test_too_many_constraints(self):
        constraints = [{"expression": f"x1 <= {i}", "name": f"c{i}"} for i in range(55)]
        result = self.tool._run(
            json.dumps(
                {
                    "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                    "objective": {"sense": "max", "expression": "x1"},
                    "constraints": constraints,
                }
            )
        )
        assert "Demasiadas" in result or "Error" in result

    def test_empty_objective_expression(self):
        result = self.tool._run(
            json.dumps(
                {
                    "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                    "objective": {"sense": "max", "expression": ""},
                    "constraints": [],
                }
            )
        )
        assert "Error" in result

    def test_variable_without_name(self):
        result = self.tool._run(
            json.dumps(
                {
                    "variables": [{"type": "continuous", "lower": 0}],
                    "objective": {"sense": "max", "expression": "x1"},
                    "constraints": [],
                }
            )
        )
        assert "Error" in result

    def test_empty_constraint_expression(self):
        result = self.tool._run(
            json.dumps(
                {
                    "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                    "objective": {"sense": "max", "expression": "x1"},
                    "constraints": [{"expression": "", "name": "c1"}],
                }
            )
        )
        assert "Error" in result


class TestParseHelpers:
    def setup_method(self):
        self.tool = ProblemSolverTool()

    def test_parse_variables(self):
        vars_def = [
            {"name": "x1", "type": "continuous", "lower": 0, "upper": 10},
            {"name": "y1", "type": "binary"},
            {"name": "z1", "type": "entera", "lower": 0},
        ]
        names, types, bounds = self.tool._parse_variables(vars_def)
        assert names == ["x1", "y1", "z1"]
        assert types == ["continuous", "binary", "integer"]
        assert bounds[1] == (0, 1)  # binary

    def test_parse_linear_expression(self):
        coeffs = self.tool._parse_linear_expression("3*x1 + 5*x2", ["x1", "x2"])
        assert coeffs == [3.0, 5.0]

    def test_parse_linear_expression_negative(self):
        coeffs = self.tool._parse_linear_expression("3*x1 - 2*x2", ["x1", "x2"])
        assert coeffs == [3.0, -2.0]

    def test_parse_term_constant(self):
        coef, var = self.tool._parse_term("42", ["x1"])
        assert coef == 42.0
        assert var is None

    def test_parse_term_bare_variable(self):
        coef, var = self.tool._parse_term("x1", ["x1"])
        assert coef == 1.0
        assert var == "x1"

    def test_parse_term_negative_variable(self):
        coef, var = self.tool._parse_term("-x1", ["x1"])
        assert coef == -1.0
        assert var == "x1"

    def test_parse_objective_maximization(self):
        coeffs, is_max = self.tool._parse_objective(
            {"sense": "maximize", "expression": "3*x1 + 5*x2"},
            ["x1", "x2"],
        )
        assert is_max is True
        # scipy minimizes, so coefficients are negated
        assert coeffs == [-3.0, -5.0]

    def test_parse_objective_minimization(self):
        coeffs, is_max = self.tool._parse_objective(
            {"sense": "minimize", "expression": "3*x1 + 5*x2"},
            ["x1", "x2"],
        )
        assert is_max is False
        assert coeffs == [3.0, 5.0]

    def test_parse_constraints_leq(self):
        constraints = [{"expression": "x1 + 2*x2 <= 10", "name": "r1"}]
        a_ub, b_ub, a_eq, b_eq, names = self.tool._parse_constraints(
            constraints, ["x1", "x2"]
        )
        assert len(a_ub) == 1
        assert b_ub == [10.0]
        assert names == ["r1"]

    def test_parse_constraints_geq(self):
        constraints = [{"expression": "x1 + x2 >= 4", "name": "demand"}]
        a_ub, b_ub, a_eq, b_eq, names = self.tool._parse_constraints(
            constraints, ["x1", "x2"]
        )
        # >= gets negated to <=
        assert len(a_ub) == 1
        assert a_ub[0] == [-1.0, -1.0]
        assert b_ub == [-4.0]

    def test_format_solution_infeasible(self):
        result = ProblemSolverTool._format_solution(
            {"status": "infeasible", "message": "No feasible"}, ["x1"], ["c1"], True
        )
        assert "Infactible" in result

    def test_format_solution_unbounded(self):
        result = ProblemSolverTool._format_solution(
            {"status": "unbounded", "message": "Unbounded"}, ["x1"], ["c1"], True
        )
        assert "No Acotado" in result

    def test_format_solution_error(self):
        result = ProblemSolverTool._format_solution(
            {"status": "error", "message": "Something failed"}, ["x1"], ["c1"], True
        )
        assert "Error" in result
