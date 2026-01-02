"""
Model Validator Tool for Mathematical Modeling.

This tool validates optimization model formulations, checking for
syntactic correctness and logical consistency.
"""

import json
import logging
import re
from typing import Any, ClassVar

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class ModelValidatorTool(BaseTool):
    """
    Tool for validating optimization model formulations.

    Checks:
    - Variable definitions (names, types, bounds)
    - Objective function syntax and variable references
    - Constraint syntax and variable references
    - Logical consistency
    """

    name: str = "model_validator"
    description: str = """Valida una formulación de modelo de optimización.

Entrada: JSON con la siguiente estructura:
{
  "variables": [
    {"name": "x1", "type": "continuous", "lower": 0},
    {"name": "x2", "type": "integer", "lower": 0, "upper": 10}
  ],
  "objective": {
    "sense": "maximize",  // o "minimize"
    "expression": "3*x1 + 5*x2"
  },
  "constraints": [
    {"expression": "x1 + 2*x2 <= 10", "name": "recurso1"},
    {"expression": "2*x1 + x2 >= 4", "name": "demanda"}
  ]
}

Tipos de variables válidos: "continuous", "integer", "binary"
Operadores de restricción válidos: <=, >=, =, <, >

Retorna: Resultado de validación con errores, advertencias y resumen."""

    model_config = {"arbitrary_types_allowed": True}

    # Valid variable types
    VALID_TYPES: ClassVar[set[str]] = {"continuous", "integer", "binary", "continua", "entera", "binaria"}
    TYPE_MAPPING: ClassVar[dict[str, str]] = {
        "continua": "continuous",
        "entera": "integer",
        "binaria": "binary",
    }

    # Valid objective senses
    VALID_SENSES: ClassVar[set[str]] = {"maximize", "minimize", "max", "min", "maximizar", "minimizar"}
    SENSE_MAPPING: ClassVar[dict[str, str]] = {
        "max": "maximize",
        "min": "minimize",
        "maximizar": "maximize",
        "minimizar": "minimize",
    }

    def _run(self, model_json: str) -> str:
        """
        Validate the optimization model.

        Args:
            model_json: JSON string with model specification

        Returns:
            Validation result as formatted string
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Parse JSON
        try:
            model = json.loads(model_json)
        except json.JSONDecodeError as e:
            return self._format_result(
                valid=False,
                errors=[f"Error al parsear JSON: {str(e)}"],
                warnings=[],
                summary="El modelo no pudo ser parseado"
            )

        # Validate structure
        if not isinstance(model, dict):
            return self._format_result(
                valid=False,
                errors=["El modelo debe ser un objeto JSON"],
                warnings=[],
                summary="Estructura inválida"
            )

        # Extract components
        variables = model.get("variables", [])
        objective = model.get("objective", {})
        constraints = model.get("constraints", [])

        # Validate variables
        var_errors, var_warnings, valid_vars = self._validate_variables(variables)
        errors.extend(var_errors)
        warnings.extend(var_warnings)

        # Validate objective
        obj_errors, obj_warnings = self._validate_objective(objective, valid_vars)
        errors.extend(obj_errors)
        warnings.extend(obj_warnings)

        # Validate constraints
        const_errors, const_warnings = self._validate_constraints(constraints, valid_vars)
        errors.extend(const_errors)
        warnings.extend(const_warnings)

        # Generate summary
        is_valid = len(errors) == 0
        summary = self._generate_summary(
            is_valid=is_valid,
            num_vars=len(valid_vars),
            num_constraints=len(constraints),
            objective_sense=objective.get("sense", "no especificado")
        )

        return self._format_result(
            valid=is_valid,
            errors=errors,
            warnings=warnings,
            summary=summary
        )

    def _validate_variables(
        self, variables: list[dict[str, Any]]
    ) -> tuple[list[str], list[str], set[str]]:
        """
        Validate variable definitions.

        Returns:
            Tuple of (errors, warnings, valid_variable_names)
        """
        errors: list[str] = []
        warnings: list[str] = []
        valid_vars: set[str] = set()

        if not variables:
            errors.append("No se definieron variables de decisión")
            return errors, warnings, valid_vars

        if not isinstance(variables, list):
            errors.append("'variables' debe ser una lista")
            return errors, warnings, valid_vars

        seen_names: set[str] = set()

        for i, var in enumerate(variables):
            if not isinstance(var, dict):
                errors.append(f"Variable {i+1}: debe ser un objeto con 'name' y 'type'")
                continue

            # Check name
            name = var.get("name")
            if not name:
                errors.append(f"Variable {i+1}: falta el nombre ('name')")
                continue

            if not isinstance(name, str):
                errors.append(f"Variable {i+1}: el nombre debe ser texto")
                continue

            # Check for a valid variable name pattern
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
                errors.append(
                    f"Variable '{name}': nombre inválido. "
                    "Use letras, números y guiones bajos (empezando con letra)"
                )
                continue

            # Check for duplicates
            if name in seen_names:
                errors.append(f"Variable '{name}': nombre duplicado")
                continue
            seen_names.add(name)

            # Check type
            var_type = var.get("type", "").lower()
            if not var_type:
                warnings.append(f"Variable '{name}': no se especificó tipo, asumiendo 'continuous'")
                var_type = "continuous"
            elif var_type in self.TYPE_MAPPING:
                var_type = self.TYPE_MAPPING[var_type]
            elif var_type not in self.VALID_TYPES:
                errors.append(
                    f"Variable '{name}': tipo '{var_type}' inválido. "
                    f"Use: continuous, integer, binary"
                )
                continue

            # Validate bounds
            lower = var.get("lower")
            upper = var.get("upper")

            if var_type == "binary":
                if lower is not None and lower != 0:
                    warnings.append(f"Variable binaria '{name}': cota inferior ignorada (será 0)")
                if upper is not None and upper != 1:
                    warnings.append(f"Variable binaria '{name}': cota superior ignorada (será 1)")
            else:
                if lower is None and var_type != "binary":
                    warnings.append(f"Variable '{name}': sin cota inferior definida")
                if upper is None:
                    # This is often fine, just informational
                    pass

                if lower is not None and upper is not None:
                    if lower > upper:
                        errors.append(
                            f"Variable '{name}': cota inferior ({lower}) > cota superior ({upper})"
                        )
                        continue

            valid_vars.add(name)

        return errors, warnings, valid_vars

    def _validate_objective(
        self, objective: dict[str, Any], valid_vars: set[str]
    ) -> tuple[list[str], list[str]]:
        """
        Validate objective function.

        Returns:
            Tuple of (errors, warnings)
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not objective:
            errors.append("No se definió función objetivo")
            return errors, warnings

        if not isinstance(objective, dict):
            errors.append("'objective' debe ser un objeto con 'sense' y 'expression'")
            return errors, warnings

        # Check sense
        sense = objective.get("sense", "").lower()
        if not sense:
            errors.append("Función objetivo: falta 'sense' (maximize/minimize)")
        elif sense in self.SENSE_MAPPING:
            pass  # Valid after mapping
        elif sense not in self.VALID_SENSES:
            errors.append(
                f"Función objetivo: sentido '{sense}' inválido. "
                "Use: maximize, minimize, max, min"
            )

        # Check expression
        expression = objective.get("expression", "")
        if not expression:
            errors.append("Función objetivo: falta 'expression'")
        else:
            expr_errors, expr_warnings = self._validate_expression(
                expression, valid_vars, "Función objetivo"
            )
            errors.extend(expr_errors)
            warnings.extend(expr_warnings)

        return errors, warnings

    def _validate_constraints(
        self, constraints: list[dict[str, Any]], valid_vars: set[str]
    ) -> tuple[list[str], list[str]]:
        """
        Validate constraints.

        Returns:
            Tuple of (errors, warnings)
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not constraints:
            warnings.append("No se definieron restricciones (modelo sin restricciones)")
            return errors, warnings

        if not isinstance(constraints, list):
            errors.append("'constraints' debe ser una lista")
            return errors, warnings

        seen_names: set[str] = set()
        constraint_operators = ["<=", ">=", "==", "=", "<", ">"]

        for i, constraint in enumerate(constraints):
            if not isinstance(constraint, dict):
                errors.append(f"Restricción {i+1}: debe ser un objeto con 'expression'")
                continue

            # Get a constraint name or generate one
            name = constraint.get("name", f"restriccion_{i+1}")
            if name in seen_names:
                warnings.append(f"Restricción '{name}': nombre duplicado")
            seen_names.add(name)

            # Check expression
            expression = constraint.get("expression", "")
            if not expression:
                errors.append(f"Restricción '{name}': falta 'expression'")
                continue

            # Check for comparison operator
            has_operator = any(op in expression for op in constraint_operators)
            if not has_operator:
                errors.append(
                    f"Restricción '{name}': falta operador de comparación (<=, >=, =)"
                )
                continue

            # Validate the expression
            expr_errors, expr_warnings = self._validate_constraint_expression(
                expression, valid_vars, name
            )
            errors.extend(expr_errors)
            warnings.extend(expr_warnings)

        return errors, warnings

    @staticmethod
    def _validate_expression(
            expression: str, valid_vars: set[str], context: str
    ) -> tuple[list[str], list[str]]:
        """
        Validate a mathematical expression (objective or LHS of constraint).

        Returns:
            Tuple of (errors, warnings)
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Extract variable names from expression
        # Pattern matches variable names (not numbers)
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        found_vars = set(re.findall(var_pattern, expression))

        # Remove common function names and constants
        reserved_words = {'sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'abs', 'max', 'min', 'sum'}
        found_vars -= reserved_words

        # Check if all variables are defined
        undefined = found_vars - valid_vars
        if undefined:
            errors.append(
                f"{context}: variables no definidas: {', '.join(sorted(undefined))}"
            )

        # Check for empty expression after removing spaces
        if not expression.strip():
            errors.append(f"{context}: expresión vacía")

        return errors, warnings

    def _validate_constraint_expression(
        self, expression: str, valid_vars: set[str], constraint_name: str
    ) -> tuple[list[str], list[str]]:
        """
        Validate a constraint expression (includes comparison operator).

        Returns:
            Tuple of (errors, warnings)
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Split by comparison operator
        operators = ["<=", ">=", "==", "=", "<", ">"]
        parts = None
        used_op = None

        for op in operators:
            if op in expression:
                parts = expression.split(op)
                used_op = op
                break

        if parts is None or len(parts) != 2:
            errors.append(
                f"Restricción '{constraint_name}': formato inválido. "
                "Use: expresión <= valor, expresión >= valor, o expresión = valor"
            )
            return errors, warnings

        lhs, rhs = parts[0].strip(), parts[1].strip()

        # Validate LHS
        lhs_errors, lhs_warnings = self._validate_expression(
            lhs, valid_vars, f"Restricción '{constraint_name}' (lado izquierdo)"
        )
        errors.extend(lhs_errors)
        warnings.extend(lhs_warnings)

        # Validate RHS (should be a number or simple expression)
        rhs_errors, rhs_warnings = self._validate_expression(
            rhs, valid_vars, f"Restricción '{constraint_name}' (lado derecho)"
        )
        errors.extend(rhs_errors)
        warnings.extend(rhs_warnings)

        # Warn about strict inequalities
        if used_op in ["<", ">"]:
            warnings.append(
                f"Restricción '{constraint_name}': desigualdad estricta ({used_op}). "
                "En optimización es más común usar <= o >="
            )

        return errors, warnings

    @staticmethod
    def _generate_summary(
            is_valid: bool, num_vars: int, num_constraints: int, objective_sense: str
    ) -> str:
        """Generate a summary of the validation."""
        if is_valid:
            sense_text = "maximización" if "max" in objective_sense.lower() else "minimización"
            return (
                f"Modelo válido: {num_vars} variables, "
                f"{num_constraints} restricciones, "
                f"objetivo de {sense_text}"
            )
        else:
            return "Modelo inválido: revise los errores indicados"

    @staticmethod
    def _format_result(
            valid: bool, errors: list[str], warnings: list[str], summary: str
    ) -> str:
        """Format the validation result as a readable string."""
        result = f"""**Resultado de Validación**

**Estado:** {"✅ Válido" if valid else "❌ Inválido"}

**Resumen:** {summary}
"""

        if errors:
            result += "\n**Errores:**\n"
            for error in errors:
                result += f"- ❌ {error}\n"

        if warnings:
            result += "\n**Advertencias:**\n"
            for warning in warnings:
                result += f"- ⚠️ {warning}\n"

        if valid and not warnings:
            result += "\n✅ El modelo está listo para ser resuelto."

        return result

    async def _arun(self, model_json: str) -> str:
        """Async version - just calls sync version since no IO is async."""
        return self._run(model_json)
