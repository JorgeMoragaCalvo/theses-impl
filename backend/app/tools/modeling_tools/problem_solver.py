"""
Problem Solver Tool for Mathematical Modeling.

This tool solves small LP/IP optimization problems to demonstrate
what a student's formulation produces.
"""

import json
import logging
import re
from typing import Any, ClassVar

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# Try to import scipy - gracefully handle if not installed
try:
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, linprog, milp
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    np = None
    Bounds = None
    LinearConstraint = None
    linprog = None
    milp = None
    logger.warning("scipy not installed - ProblemSolverTool will have limited functionality")


class ProblemSolverTool(BaseTool):
    """
    Tool for solving small LP/IP optimization problems.

    Uses scipy.optimize.linprog for LP and scipy.optimize.milp for IP/MIP.
    Limited to 20 variables for computational safety.
    """

    name: str = "problem_solver"
    description: str = """Resuelve problemas de optimización LP/IP pequeños (máximo 20 variables).

Entrada: JSON con la siguiente estructura:
{
  "variables": [
    {"name": "x1", "type": "continuous", "lower": 0},
    {"name": "x2", "type": "integer", "lower": 0, "upper": 10}
  ],
  "objective": {
    "sense": "maximize",
    "expression": "3*x1 + 5*x2"
  },
  "constraints": [
    {"expression": "x1 + 2*x2 <= 10", "name": "recurso1"},
    {"expression": "2*x1 + x2 <= 8", "name": "recurso2"}
  ]
}

Retorna: Solución óptima con valores de variables, valor objetivo e interpretación.
Estados posibles: optimal, infeasible, unbounded, error."""

    model_config = {"arbitrary_types_allowed": True}

    MAX_VARIABLES: ClassVar[int] = 20
    MAX_CONSTRAINTS: ClassVar[int] = 50

    def _run(self, model_json: str) -> str:
        """
        Solve the optimization problem.

        Args:
            model_json: JSON string with model specification

        Returns:
            Solution result as formatted string
        """
        if not SCIPY_AVAILABLE:
            return self._format_error(
                "scipy no está instalado. Instale con: pip install scipy"
            )

        # Parse JSON
        try:
            model = json.loads(model_json)
        except json.JSONDecodeError as e:
            return self._format_error(f"Error al parsear JSON: {str(e)}")

        # Extract and validate components
        variables = model.get("variables", [])
        objective = model.get("objective", {})
        constraints = model.get("constraints", [])

        # Check limits
        if len(variables) > self.MAX_VARIABLES:
            return self._format_error(
                f"Demasiadas variables ({len(variables)}). Máximo permitido: {self.MAX_VARIABLES}"
            )

        if len(constraints) > self.MAX_CONSTRAINTS:
            return self._format_error(
                f"Demasiadas restricciones ({len(constraints)}). Máximo permitido: {self.MAX_CONSTRAINTS}"
            )

        if not variables:
            return self._format_error("No se definieron variables")

        if not objective:
            return self._format_error("No se definió función objetivo")

        try:
            # Parse the model into scipy format
            var_names, var_types, bounds = self._parse_variables(variables)
            c, is_maximization = self._parse_objective(objective, var_names)
            a_ub, b_ub, a_eq, b_eq, constraint_names = self._parse_constraints(
                constraints, var_names
            )

            # Determine if this is an IP or LP problem
            has_integer = any(t in ("integer", "binary") for t in var_types)

            if has_integer:
                result = self._solve_milp(
                    c, a_ub, b_ub, a_eq, b_eq, bounds, var_types, is_maximization
                )
            else:
                result = self._solve_lp(
                    c, a_ub, b_ub, a_eq, b_eq, bounds, is_maximization
                )

            return self._format_solution(
                result, var_names, constraint_names, is_maximization
            )

        except ValueError as e:
            return self._format_error(f"Error en la formulación: {str(e)}")
        except Exception as e:
            logger.exception("Error solving optimization problem")
            return self._format_error(f"Error al resolver: {str(e)}")

    @staticmethod
    def _parse_variables(
            variables: list[dict[str, Any]]
    ) -> tuple[list[str], list[str], list[tuple[float | None, float | None]]]:
        """
        Parse variable definitions.

        Returns:
            Tuple of (names, types, bounds)
        """
        names = []
        types = []
        bounds = []

        type_mapping = {
            "continuous": "continuous",
            "continua": "continuous",
            "integer": "integer",
            "entera": "integer",
            "binary": "binary",
            "binaria": "binary",
        }

        for var in variables:
            name = var.get("name")
            if not name:
                raise ValueError("Variable sin nombre")
            names.append(name)

            var_type = var.get("type", "continuous").lower()
            var_type = type_mapping.get(var_type, "continuous")
            types.append(var_type)

            if var_type == "binary":
                bounds.append((0, 1))
            else:
                lower = var.get("lower")
                upper = var.get("upper")
                # Convert None to appropriate scipy bounds
                lb = float(lower) if lower is not None else 0.0  # Default lower = 0
                ub = float(upper) if upper is not None else None
                bounds.append((lb, ub))

        return names, types, bounds

    def _parse_objective(
        self, objective: dict[str, Any], var_names: list[str]
    ) -> tuple[list[float], bool]:
        """
        Parse objective function.

        Returns:
            Tuple of (coefficient_vector, is_maximization)
        """
        sense = objective.get("sense", "minimize").lower()
        is_maximization = sense in ("maximize", "max", "maximizar")

        expression = objective.get("expression", "")
        if not expression:
            raise ValueError("Función objetivo vacía")

        coefficients = self._parse_linear_expression(expression, var_names)

        # scipy minimizes, so negate for maximization
        if is_maximization:
            coefficients = [-c for c in coefficients]

        return coefficients, is_maximization

    def _parse_constraints(
        self, constraints: list[dict[str, Any]], var_names: list[str]
    ) -> tuple[list[list[float]], list[float], list[list[float]], list[float], list[str]]:
        """
        Parse constraints.

        Returns:
            Tuple of (A_ub, b_ub, A_eq, b_eq, constraint_names)
        """
        a_ub: list[list[float]] = []
        b_ub: list[float] = []
        a_eq: list[list[float]] = []
        b_eq: list[float] = []
        names: list[str] = []

        for i, constraint in enumerate(constraints):
            name = constraint.get("name", f"c{i+1}")
            names.append(name)

            expression = constraint.get("expression", "")
            if not expression:
                raise ValueError(f"Restricción '{name}' vacía")

            # Parse the constraint
            lhs, rhs, sense = self._parse_constraint_expression(expression, var_names)

            if sense == "<=":
                a_ub.append(lhs)
                b_ub.append(rhs)
            elif sense == ">=":
                # Convert >= to <= by negating
                a_ub.append([-c for c in lhs])
                b_ub.append(-rhs)
            elif sense == "=":
                a_eq.append(lhs)
                b_eq.append(rhs)

        return a_ub, b_ub, a_eq, b_eq, names

    def _parse_linear_expression(
        self, expression: str, var_names: list[str]
    ) -> list[float]:
        """
        Parse a linear expression into a coefficient vector.

        Example: "3*x1 + 5*x2 - 2*x3" -> [3.0, 5.0, -2.0]
        """
        coefficients = [0.0] * len(var_names)

        # Normalize expression
        expr = expression.replace(" ", "").replace("-", "+-")

        # Split by + (handling leading minus)
        terms = [t for t in expr.split("+") if t]

        for term in terms:
            if not term:
                continue

            coef, var = self._parse_term(term, var_names)
            if var is not None:
                try:
                    idx = var_names.index(var)
                    coefficients[idx] += coef
                except ValueError:
                    raise ValueError(f"Variable '{var}' no definida")

        return coefficients

    @staticmethod
    def _parse_term(
            term: str, var_names: list[str]
    ) -> tuple[float, str | None]:
        """
        Parse a single term like "3*x1", "-x2", "5", "x1".

        Returns:
            Tuple of (coefficient, variable_name, or None if constant)
        """
        term = term.strip()

        if not term:
            return 0.0, None

        # Check if it's just a number (constant term)
        try:
            return float(term), None
        except ValueError:
            pass

        # Find variable name in term
        var_found = None
        for var in sorted(var_names, key=len, reverse=True):  # Longest first
            if var in term:
                var_found = var
                break

        if var_found is None:
            # Might be an unknown variable or just a number
            try:
                return float(term), None
            except ValueError:
                # Extract what looks like a variable
                match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)', term)
                if match:
                    raise ValueError(f"Variable '{match.group(1)}' no definida")
                raise ValueError(f"Término inválido: '{term}'")

        # Extract coefficient
        # Remove variable and * to get coefficient
        coef_str = term.replace(var_found, "").replace("*", "").strip()

        if not coef_str or coef_str == "+":
            coef = 1.0
        elif coef_str == "-":
            coef = -1.0
        else:
            try:
                coef = float(coef_str)
            except ValueError:
                raise ValueError(f"Coeficiente inválido en término: '{term}'")

        return coef, var_found

    def _parse_constraint_expression(
        self, expression: str, var_names: list[str]
    ) -> tuple[list[float], float, str]:
        """
        Parse a constraint expression.

        Returns:
            Tuple of (lhs_coefficients, rhs_value, sense)
        """
        # Find the operator
        operators = ["<=", ">=", "==", "="]
        op_found = None
        parts = None

        for op in operators:
            if op in expression:
                parts = expression.split(op, 1)
                op_found = "=" if op == "==" else op
                break

        if parts is None or len(parts) != 2:
            raise ValueError(f"Formato de restricción inválido: '{expression}'")

        lhs_expr, rhs_expr = parts[0].strip(), parts[1].strip()

        # Parse LHS
        lhs = self._parse_linear_expression(lhs_expr, var_names)

        # Parse RHS (should be a constant but might have variables)
        rhs_coeffs = self._parse_linear_expression(rhs_expr, var_names)

        # Check if RHS has variables (move them to LHS)
        has_rhs_vars = any(c != 0 for c in rhs_coeffs)
        if has_rhs_vars:
            # Move RHS variables to LHS: lhs - rhs_vars <= rhs_constant
            lhs = [l - r for l, r in zip(lhs, rhs_coeffs)]

        # Get RHS constant
        try:
            # Try to evaluate RHS as a pure number first
            rhs_value = float(rhs_expr)
        except ValueError:
            # RHS has variables, constant is 0 after moving them
            rhs_value = 0.0

        return lhs, rhs_value, op_found

    @staticmethod
    def _solve_lp(
            c: list[float],
        a_ub: list[list[float]],
        b_ub: list[float],
        a_eq: list[list[float]],
        b_eq: list[float],
        bounds: list[tuple[float | None, float | None]],
        is_maximization: bool
    ) -> dict[str, Any]:
        """Solve LP using scipy.optimize.linprog."""
        result = linprog(
            c=c,
            A_ub=a_ub if a_ub else None,
            b_ub=b_ub if b_ub else None,
            A_eq=a_eq if a_eq else None,
            b_eq=b_eq if b_eq else None,
            bounds=bounds,
            method='highs'
        )

        if result.success:
            obj_value = -result.fun if is_maximization else result.fun
            return {
                "status": "optimal",
                "objective_value": obj_value,
                "variables": result.x.tolist(),
                "slack": result.slack.tolist() if hasattr(result, 'slack') and result.slack is not None else None
            }
        else:
            # Determine failure reason
            if "infeasible" in result.message.lower():
                return {"status": "infeasible", "message": result.message}
            elif "unbounded" in result.message.lower():
                return {"status": "unbounded", "message": result.message}
            else:
                return {"status": "error", "message": result.message}

    @staticmethod
    def _solve_milp(
            c: list[float],
        a_ub: list[list[float]],
        b_ub: list[float],
        a_eq: list[list[float]],
        b_eq: list[float],
        bounds: list[tuple[float | None, float | None]],
        var_types: list[str],
        is_maximization: bool
    ) -> dict[str, Any]:
        """Solve MIP using scipy.optimize.milp."""
        n = len(c)

        # Create an integrality array (0=continuous, 1=integer)
        integrality = np.zeros(n, dtype=int)
        for i, vtype in enumerate(var_types):
            if vtype in ("integer", "binary"):
                integrality[i] = 1

        # Create a bounds object
        lb = np.array([b[0] if b[0] is not None else -np.inf for b in bounds])
        ub = np.array([b[1] if b[1] is not None else np.inf for b in bounds])
        scipy_bounds = Bounds(lb, ub)

        # Create constraints
        constraints = []

        if a_ub:
            a_ub_arr = np.array(a_ub)
            b_ub_arr = np.array(b_ub)
            constraints.append(LinearConstraint(a_ub_arr, -np.inf, b_ub_arr))

        if a_eq:
            a_eq_arr = np.array(a_eq)
            b_eq_arr = np.array(b_eq)
            constraints.append(LinearConstraint(a_eq_arr, b_eq_arr, b_eq_arr))

        result = milp(
            c=np.array(c),
            constraints=constraints if constraints else None,
            integrality=integrality,
            bounds=scipy_bounds
        )

        if result.success:
            obj_value = -result.fun if is_maximization else result.fun
            return {
                "status": "optimal",
                "objective_value": obj_value,
                "variables": result.x.tolist()
            }
        else:
            if "infeasible" in str(result.message).lower():
                return {"status": "infeasible", "message": str(result.message)}
            elif "unbounded" in str(result.message).lower():
                return {"status": "unbounded", "message": str(result.message)}
            else:
                return {"status": "error", "message": str(result.message)}

    @staticmethod
    def _format_solution(
            result: dict[str, Any],
        var_names: list[str],
        constraint_names: list[str],
        is_maximization: bool
    ) -> str:
        """Format the solution result."""
        status = result.get("status")

        if status == "optimal":
            sense_text = "Maximización" if is_maximization else "Minimización"
            obj_value = result["objective_value"]
            variables = result["variables"]

            output = f"""**Solución Óptima Encontrada** ✅

**Tipo:** {sense_text}
**Valor Óptimo:** {obj_value:.4f}

**Valores de las Variables:**
"""
            for name, value in zip(var_names, variables):
                # Round very small values to 0 for display
                display_val = value if abs(value) > 1e-8 else 0.0
                output += f"- {name} = {display_val:.4f}\n"

            # Add slack information if available
            slack = result.get("slack")
            if slack:
                output += "\n**Holguras (Slack):**\n"
                for i, (name, s) in enumerate(zip(constraint_names, slack)):
                    if s < 1e-8:
                        output += f"- {name}: 0 (restricción activa/binding)\n"
                    else:
                        output += f"- {name}: {s:.4f}\n"

            output += "\n*La solución satisface todas las restricciones.*"
            return output

        elif status == "infeasible":
            return """**Problema Infactible** ❌

No existe solución factible que satisfaga todas las restricciones simultáneamente.

**Posibles causas:**
- Restricciones contradictorias
- Cotas de variables incompatibles
- Error en la formulación del modelo

**Sugerencia:** Revisa las restricciones para identificar conflictos."""

        elif status == "unbounded":
            sense_text = "maximizar" if is_maximization else "minimizar"
            return f"""**Problema No Acotado** ⚠️

La función objetivo puede {sense_text} indefinidamente.

**Posibles causas:**
- Falta alguna restricción importante
- Las restricciones no limitan suficientemente las variables
- El problema está mal formulado

**Sugerencia:** Verifica que todas las restricciones necesarias estén incluidas."""

        else:
            message = result.get("message", "Error desconocido")
            return f"""**Error al Resolver** ❌

{message}

Por favor verifica la formulación del modelo."""

    @staticmethod
    def _format_error(message: str) -> str:
        """Format an error message."""
        return f"""**Error** ❌

{message}

Por favor verifica la entrada y vuelve a intentar."""

    async def _arun(self, model_json: str) -> str:
        """Async version - just calls sync version."""
        return self._run(model_json)
