"""
Shared LP/IP model parsing helpers.

These functions parse the common JSON model contract used by
``ProblemSolverTool`` and ``SimplexSolverTool`` (variables, objective,
constraints with linear expressions). Keeping them in one module ensures a
single source of truth for the expression parser.

Note on the sign convention: ``parse_objective_coefficients`` returns the *raw*
(unnegated) objective coefficients plus ``is_maximization``. Each tool applies
its own convention — ``ProblemSolverTool`` negates for scipy (which minimizes),
while ``SimplexSolverTool`` keeps the natural goal row.
"""

import re
from typing import Any


def parse_variables(
    variables: list[dict[str, Any]],
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
            # Convert None to appropriate bounds
            lb = float(lower) if lower is not None else 0.0  # Default lower = 0
            ub = float(upper) if upper is not None else None
            bounds.append((lb, ub))

    return names, types, bounds


def parse_objective_coefficients(
    objective: dict[str, Any], var_names: list[str]
) -> tuple[list[float], bool]:
    """
    Parse objective function into raw (unnegated) coefficients.

    Returns:
        Tuple of (coefficient_vector, is_maximization)
    """
    sense = objective.get("sense", "minimize").lower()
    is_maximization = sense in ("maximize", "max", "maximizar")

    expression = objective.get("expression", "")
    if not expression:
        raise ValueError("Función objetivo vacía")

    coefficients = parse_linear_expression(expression, var_names)
    return coefficients, is_maximization


def parse_constraints(
    constraints: list[dict[str, Any]], var_names: list[str]
) -> tuple[
    list[list[float]], list[float], list[list[float]], list[float], list[str]
]:
    """
    Parse constraints into scipy-style ``A_ub``/``A_eq`` split.

    ``>=`` constraints are converted to ``<=`` by negation.

    Returns:
        Tuple of (A_ub, b_ub, A_eq, b_eq, constraint_names)
    """
    a_ub: list[list[float]] = []
    b_ub: list[float] = []
    a_eq: list[list[float]] = []
    b_eq: list[float] = []
    names: list[str] = []

    for i, constraint in enumerate(constraints):
        name = constraint.get("name", f"c{i + 1}")
        names.append(name)

        expression = constraint.get("expression", "")
        if not expression:
            raise ValueError(f"Restricción '{name}' vacía")

        lhs, rhs, sense = parse_constraint_expression(expression, var_names)

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


def parse_linear_expression(expression: str, var_names: list[str]) -> list[float]:
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

        coef, var = parse_term(term, var_names)
        if var is not None:
            try:
                idx = var_names.index(var)
                coefficients[idx] += coef
            except ValueError:
                raise ValueError(f"Variable '{var}' no definida")

    return coefficients


def parse_term(term: str, var_names: list[str]) -> tuple[float, str | None]:
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

    # Find a variable name in the term
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
            match = re.search(r"([a-zA-Z_][a-zA-Z0-9_]*)", term)
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


def parse_constraint_expression(
    expression: str, var_names: list[str]
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
    lhs = parse_linear_expression(lhs_expr, var_names)

    # Parse RHS (should be a constant but might have variables)
    rhs_coeffs = parse_linear_expression(rhs_expr, var_names)

    # Check if RHS has variables (move them to LHS)
    has_rhs_vars = any(c != 0 for c in rhs_coeffs)
    if has_rhs_vars:
        # Move RHS variables to LHS: lhs - rhs_vars <= rhs_constant
        lhs = [
            lhs_coef - rhs_coef
            for lhs_coef, rhs_coef in zip(lhs, rhs_coeffs, strict=True)
        ]
    # Get RHS constant
    try:
        # Try to evaluate RHS as a pure number first
        rhs_value = float(rhs_expr)
    except ValueError:
        # RHS has variables, constant is 0 after moving them
        rhs_value = 0.0

    return lhs, rhs_value, op_found
