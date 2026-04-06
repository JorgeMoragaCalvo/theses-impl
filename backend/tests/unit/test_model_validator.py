"""
Unit tests for ModelValidatorTool — validation of optimization model formulations.
"""

import json

from app.tools.modeling_tools.model_validator import ModelValidatorTool


def make_model_json(**overrides):
    """Helper to build a valid model JSON string."""
    model = {
        "variables": [
            {"name": "x1", "type": "continuous", "lower": 0},
            {"name": "x2", "type": "continuous", "lower": 0},
        ],
        "objective": {"sense": "maximize", "expression": "3*x1 + 5*x2"},
        "constraints": [
            {"expression": "x1 + 2*x2 <= 10", "name": "resource"},
        ],
    }
    model.update(overrides)
    return json.dumps(model)


class TestModelValidatorBasic:
    def setup_method(self):
        self.tool = ModelValidatorTool()

    def test_valid_model(self):
        result = self.tool._run(make_model_json())
        assert "Válido" in result
        assert "2 variables" in result

    def test_invalid_json(self):
        result = self.tool._run("not json {{{")
        assert "Inválido" in result or "Error" in result

    def test_non_dict_json(self):
        result = self.tool._run(json.dumps([1, 2, 3]))
        assert "Inválido" in result

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
        assert "No se definieron variables" in result

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
        assert "No se definió función objetivo" in result


class TestVariableValidation:
    def setup_method(self):
        self.tool = ModelValidatorTool()

    def test_duplicate_variable(self):
        model = json.dumps(
            {
                "variables": [
                    {"name": "x1", "type": "continuous", "lower": 0},
                    {"name": "x1", "type": "continuous", "lower": 0},
                ],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "duplicado" in result

    def test_invalid_variable_name(self):
        model = json.dumps(
            {
                "variables": [{"name": "123bad", "type": "continuous"}],
                "objective": {"sense": "max", "expression": "123bad"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "inválido" in result

    def test_missing_variable_name(self):
        model = json.dumps(
            {
                "variables": [{"type": "continuous"}],
                "objective": {"sense": "max", "expression": "x"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "falta el nombre" in result

    def test_invalid_variable_type(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "complex"}],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "inválido" in result

    def test_spanish_type_mapping(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "entera", "lower": 0}],
                "objective": {"sense": "maximizar", "expression": "x1"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "Válido" in result

    def test_binary_variable_warns_bounds(self):
        model = json.dumps(
            {
                "variables": [
                    {"name": "y1", "type": "binary", "lower": 5, "upper": 10}
                ],
                "objective": {"sense": "min", "expression": "y1"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "ignorada" in result

    def test_lower_greater_than_upper(self):
        model = json.dumps(
            {
                "variables": [
                    {"name": "x1", "type": "continuous", "lower": 10, "upper": 5}
                ],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "cota inferior" in result

    def test_no_type_defaults_continuous(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "lower": 0}],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "Válido" in result
        assert "continuous" in result or "Advertencia" in result

    def test_variable_not_dict(self):
        model = json.dumps(
            {
                "variables": ["x1"],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "debe ser un objeto" in result

    def test_variables_not_list(self):
        model = json.dumps(
            {
                "variables": "x1",
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "debe ser una lista" in result

    def test_variable_name_not_string(self):
        model = json.dumps(
            {
                "variables": [{"name": 123, "type": "continuous"}],
                "objective": {"sense": "max", "expression": "x"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "debe ser texto" in result


class TestObjectiveValidation:
    def setup_method(self):
        self.tool = ModelValidatorTool()

    def test_invalid_sense(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                "objective": {"sense": "optimize", "expression": "x1"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "inválido" in result

    def test_missing_expression(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                "objective": {"sense": "max", "expression": ""},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "falta" in result

    def test_undefined_variable_in_objective(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                "objective": {"sense": "max", "expression": "x1 + x2"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "no definidas" in result

    def test_minimize_sense(self):
        result = self.tool._run(
            make_model_json(
                objective={"sense": "minimize", "expression": "3*x1 + 5*x2"}
            )
        )
        assert "minimización" in result


class TestConstraintValidation:
    def setup_method(self):
        self.tool = ModelValidatorTool()

    def test_no_constraints_warning(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [],
            }
        )
        result = self.tool._run(model)
        assert "sin restricciones" in result

    def test_missing_operator(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [{"expression": "x1 + 5", "name": "c1"}],
            }
        )
        result = self.tool._run(model)
        assert "operador" in result

    def test_constraint_not_dict(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": ["x1 <= 5"],
            }
        )
        result = self.tool._run(model)
        assert "debe ser un objeto" in result

    def test_constraints_not_list(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": "x1 <= 5",
            }
        )
        result = self.tool._run(model)
        assert "debe ser una lista" in result

    def test_empty_constraint_expression(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [{"expression": "", "name": "c1"}],
            }
        )
        result = self.tool._run(model)
        assert "falta" in result

    def test_strict_inequality_warning(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [{"expression": "x1 < 10", "name": "c1"}],
            }
        )
        result = self.tool._run(model)
        assert "estricta" in result

    def test_duplicate_constraint_name(self):
        model = json.dumps(
            {
                "variables": [{"name": "x1", "type": "continuous", "lower": 0}],
                "objective": {"sense": "max", "expression": "x1"},
                "constraints": [
                    {"expression": "x1 <= 10", "name": "c1"},
                    {"expression": "x1 >= 0", "name": "c1"},
                ],
            }
        )
        result = self.tool._run(model)
        assert "duplicado" in result

    def test_equality_constraint(self):
        result = self.tool._run(
            make_model_json(constraints=[{"expression": "x1 + x2 = 5", "name": "eq1"}])
        )
        assert "Válido" in result


class TestAsyncRun:
    def test_arun(self):
        import asyncio

        tool = ModelValidatorTool()
        result = asyncio.new_event_loop().run_until_complete(
            tool._arun(make_model_json())
        )
        assert "Válido" in result
