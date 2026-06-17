"""
Branch-and-Bound Tool for step-by-step Integer Programming.

Unlike ``ProblemSolverTool`` (scipy ``milp``, which returns only the final
integer optimum) and ``SimplexSolverTool`` (which shows the LP *relaxation*
step by step), this tool runs an explicit **branch-and-bound** search and
returns the whole tree: every node's added branching constraint, its LP
relaxation result (``z*`` and ``x*``), and the decision taken (integer →
incumbent / pruned by bound / infeasible / branch on ``xᵢ``).

The pedagogical goal is the same as the simplex tool: the agent *presents*
a verified, computed tree instead of inventing one. Each node's LP relaxation
is solved deterministically with scipy ``linprog`` (same sign convention as
``ProblemSolverTool._solve_lp``); the parsing layer is shared via ``_lp_parsing``.
"""

import json
import logging
import math
from typing import Any, ClassVar

from langchain_core.tools import BaseTool

from ._lp_parsing import (
    parse_constraints,
    parse_objective_coefficients,
    parse_variables,
)

logger = logging.getLogger(__name__)

# Try to import scipy - gracefully handle if not installed
try:
    from scipy.optimize import linprog

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    linprog = None
    logger.warning(
        "scipy not installed - BranchAndBoundTool will have limited functionality"
    )


def _fmt(value: float) -> str:
    """Format a number compactly, snapping tiny values to 0."""
    if value is None:
        return "—"
    if abs(value) < 1e-9:
        return "0"
    return f"{value:.4g}"


class BranchAndBoundTool(BaseTool):
    """
    Tool for solving small IP/MIP problems step by step with branch-and-bound.

    Each node's LP relaxation is solved with scipy ``linprog``. Branching is
    depth-first on the most-fractional integer variable (floor child first).
    Variables marked ``integer``/``binary`` are enforced; ``binary`` is bounded
    to ``[0, 1]`` by the shared parser.
    """

    name: str = "branch_and_bound"
    description: str = """Resuelve un problema de Programación Entera (IP/MIP/binario) PASO A PASO con ramificación y acotamiento (branch and bound). Construye el árbol de búsqueda completo (máximo 10 variables).

Úsalo cuando el estudiante pida ver el árbol de branch and bound, la ramificación y el acotamiento, o resolver el problema entero "paso a paso". Para sólo el óptimo entero final usa problem_solver; para la relajación LP paso a paso (tableaus símplex) usa simplex_solver.

Entrada: JSON con la misma estructura que problem_solver (marca las variables enteras/binarias con "type"):
{
  "variables": [
    {"name": "x1", "type": "integer", "lower": 0},
    {"name": "x2", "type": "integer", "lower": 0}
  ],
  "objective": {
    "sense": "maximize",
    "expression": "5*x1 + 4*x2"
  },
  "constraints": [
    {"expression": "6*x1 + 4*x2 <= 24", "name": "r1"},
    {"expression": "x1 + 2*x2 <= 6", "name": "r2"}
  ]
}

Retorna: el árbol de búsqueda nodo por nodo (restricción de ramificación, relajación LP z* y x*, y la decisión: entero/incumbente, podado por cota, infactible o ramificar) y la solución entera óptima.
Estados posibles: óptimo, infactible (Infactible), no acotado (No Acotado), error."""

    model_config = {"arbitrary_types_allowed": True}

    MAX_VARIABLES: ClassVar[int] = 10
    MAX_CONSTRAINTS: ClassVar[int] = 50
    MAX_NODES: ClassVar[int] = 200
    MAX_DEPTH: ClassVar[int] = 30
    EPS: ClassVar[float] = 1e-9
    INT_TOL: ClassVar[float] = 1e-6

    def _run(self, model_json: str) -> str:
        """Run branch-and-bound and return a Markdown report of the tree."""
        if not SCIPY_AVAILABLE:
            return self._format_error(
                "scipy no está instalado. Instale con: pip install scipy"
            )

        try:
            model = json.loads(model_json)
        except json.JSONDecodeError as e:
            return self._format_error(f"Error al parsear JSON: {str(e)}")

        variables = model.get("variables", [])
        objective = model.get("objective", {})
        constraints = model.get("constraints", [])

        if len(variables) > self.MAX_VARIABLES:
            return self._format_error(
                f"Demasiadas variables ({len(variables)}). "
                f"Máximo permitido: {self.MAX_VARIABLES}"
            )
        if len(constraints) > self.MAX_CONSTRAINTS:
            return self._format_error(
                f"Demasiadas restricciones ({len(constraints)}). "
                f"Máximo permitido: {self.MAX_CONSTRAINTS}"
            )
        if not variables:
            return self._format_error("No se definieron variables")
        if not objective:
            return self._format_error("No se definió función objetivo")
        if not constraints:
            return self._format_error("No se definieron restricciones")

        try:
            names, types, bounds = parse_variables(variables)
            obj_coeffs, is_max = parse_objective_coefficients(objective, names)
            a_ub, b_ub, a_eq, b_eq, _cnames = parse_constraints(constraints, names)

            integer_idx = [
                i for i, t in enumerate(types) if t in ("integer", "binary")
            ]
            if not integer_idx:
                return self._format_error(
                    "El modelo no tiene variables enteras ni binarias. Para un "
                    "problema continuo usa simplex_solver (paso a paso) o "
                    "problem_solver (óptimo final)."
                )

            result = self._branch_and_bound(
                names, bounds, obj_coeffs, is_max, a_ub, b_ub, a_eq, b_eq, integer_idx
            )
            return self._format_result(result, names, obj_coeffs, is_max)

        except ValueError as e:
            return self._format_error(f"Error en la formulación: {str(e)}")
        except Exception as e:
            logger.exception("Error solving IP with branch and bound")
            return self._format_error(f"Error al resolver: {str(e)}")

    # ------------------------------------------------------------------ #
    # Branch-and-bound engine
    # ------------------------------------------------------------------ #
    def _solve_lp(
        self,
        c_min: list[float],
        a_ub: list[list[float]],
        b_ub: list[float],
        a_eq: list[list[float]],
        b_eq: list[float],
        bounds: list[tuple[float | None, float | None]],
    ) -> tuple[str, list[float] | None, float | None]:
        """Solve one node's LP relaxation with scipy ``linprog`` (minimization).

        ``c_min`` is already in minimization form. Returns (status, x, fun)
        where ``fun`` is the minimized value of ``c_min · x``.
        """
        res = linprog(
            c=c_min,
            A_ub=a_ub if a_ub else None,
            b_ub=b_ub if b_ub else None,
            A_eq=a_eq if a_eq else None,
            b_eq=b_eq if b_eq else None,
            bounds=bounds,
            method="highs",
        )
        if res.success:
            return "optimal", res.x.tolist(), float(res.fun)
        msg = str(res.message).lower()
        if "infeasible" in msg:
            return "infeasible", None, None
        if "unbounded" in msg:
            return "unbounded", None, None
        return "error", None, None

    def _most_fractional(
        self, x: list[float], integer_idx: list[int]
    ) -> int | None:
        """Return the index of the most-fractional integer variable, or None."""
        best = None
        best_score = self.INT_TOL
        for i in integer_idx:
            frac = x[i] - math.floor(x[i])
            distance = min(frac, 1.0 - frac)  # 0 at integer, 0.5 at most fractional
            if distance > best_score:
                best_score = distance
                best = i
        return best

    def _branch_and_bound(
        self,
        names: list[str],
        base_bounds: list[tuple[float | None, float | None]],
        obj_coeffs: list[float],
        is_max: bool,
        a_ub: list[list[float]],
        b_ub: list[float],
        a_eq: list[list[float]],
        b_eq: list[float],
        integer_idx: list[int],
    ) -> dict[str, Any]:
        """Run depth-first branch-and-bound, recording every visited node."""
        c_min = [-c for c in obj_coeffs] if is_max else list(obj_coeffs)
        eps = self.EPS

        incumbent_x: list[float] | None = None
        incumbent_val: float | None = None
        nodes: list[dict[str, Any]] = []

        # DFS stack of (bounds, parent_id, branch_label, depth)
        stack: list[tuple[list, int | None, str, int]] = [
            (list(base_bounds), None, "raíz", 0)
        ]
        node_counter = 0
        truncated = False
        unbounded = False

        while stack:
            if node_counter >= self.MAX_NODES:
                truncated = True
                break

            bounds, parent_id, label, depth = stack.pop()
            node_id = node_counter
            node_counter += 1

            status, x, fun = self._solve_lp(c_min, a_ub, b_ub, a_eq, b_eq, bounds)
            rec: dict[str, Any] = {
                "id": node_id,
                "parent": parent_id,
                "label": label,
                "depth": depth,
                "obj": None,
                "x": None,
                "decision": "",
            }

            if status == "infeasible":
                rec["decision"] = "infactible → podado"
                nodes.append(rec)
                continue
            if status == "unbounded":
                rec["decision"] = "relajación no acotada"
                nodes.append(rec)
                unbounded = True
                break
            if status == "error":
                rec["decision"] = "error al resolver la relajación → podado"
                nodes.append(rec)
                continue

            relax_obj = -fun if is_max else fun
            rec["obj"] = relax_obj
            rec["x"] = x

            # Prune by bound: relaxation cannot strictly improve the incumbent.
            if incumbent_val is not None and (
                (is_max and relax_obj <= incumbent_val + eps)
                or (not is_max and relax_obj >= incumbent_val - eps)
            ):
                rec["decision"] = (
                    f"cota {_fmt(relax_obj)} no mejora incumbente "
                    f"{_fmt(incumbent_val)} → podado"
                )
                nodes.append(rec)
                continue

            frac_var = self._most_fractional(x, integer_idx)
            if frac_var is None:
                # Integer-feasible: candidate solution.
                improves = incumbent_val is None or (
                    relax_obj > incumbent_val + eps
                    if is_max
                    else relax_obj < incumbent_val - eps
                )
                if improves:
                    incumbent_x = x
                    incumbent_val = relax_obj
                    rec["decision"] = (
                        f"solución entera z={_fmt(relax_obj)} → nuevo incumbente ✅"
                    )
                else:
                    rec["decision"] = (
                        f"solución entera z={_fmt(relax_obj)} (no mejora incumbente)"
                    )
                nodes.append(rec)
                continue

            # Branch on the most-fractional variable.
            value = x[frac_var]
            floor_v = math.floor(value + eps)
            ceil_v = math.ceil(value - eps)
            rec["decision"] = (
                f"{names[frac_var]} = {_fmt(value)} fraccionaria → ramificar"
            )
            nodes.append(rec)

            if depth + 1 > self.MAX_DEPTH:
                truncated = True
                continue

            lb, ub = bounds[frac_var]
            ceil_bounds = list(bounds)
            ceil_bounds[frac_var] = (float(ceil_v), ub)
            floor_bounds = list(bounds)
            floor_bounds[frac_var] = (lb, float(floor_v))

            # Push ceil first so the floor child is explored first (DFS).
            stack.append(
                (ceil_bounds, node_id, f"{names[frac_var]} ≥ {ceil_v}", depth + 1)
            )
            stack.append(
                (floor_bounds, node_id, f"{names[frac_var]} ≤ {floor_v}", depth + 1)
            )

        return {
            "nodes": nodes,
            "incumbent_x": incumbent_x,
            "incumbent_val": incumbent_val,
            "truncated": truncated,
            "unbounded": unbounded,
        }

    # ------------------------------------------------------------------ #
    # Formatting
    # ------------------------------------------------------------------ #
    def _format_result(
        self,
        result: dict[str, Any],
        names: list[str],
        obj_coeffs: list[float],
        is_max: bool,
    ) -> str:
        nodes = result["nodes"]
        parts: list[str] = ["**Ramificación y Acotamiento (Branch & Bound) paso a paso** 🌳"]

        sense_text = "Maximización" if is_max else "Minimización"
        parts.append(f"\n**Tipo:** {sense_text} · **Nodos explorados:** {len(nodes)}")

        parts.append("\n## Árbol de búsqueda")
        parts.append("| Nodo | Padre | Restricción | z (relajación) | Solución LP | Decisión |")
        parts.append("|---|---|---|---|---|---|")
        for node in nodes:
            parent = "—" if node["parent"] is None else str(node["parent"])
            x_str = self._format_point(node["x"], names)
            parts.append(
                f"| {node['id']} | {parent} | {node['label']} | "
                f"{_fmt(node['obj'])} | {x_str} | {node['decision']} |"
            )

        parts.append("\n## Resultado")
        if result["unbounded"]:
            parts.append(self._format_unbounded(is_max))
        elif result["incumbent_val"] is None:
            parts.append(self._format_infeasible())
        else:
            parts.append(
                self._format_solution(
                    names, result["incumbent_x"], result["incumbent_val"], is_max
                )
            )

        if result["truncated"]:
            parts.append(
                "\n⚠️ **Búsqueda truncada**: se alcanzó el límite de nodos/profundidad. "
                "La solución mostrada es la mejor encontrada hasta ese punto; usa "
                "problem_solver para el óptimo final garantizado."
            )

        return "\n".join(parts)

    @staticmethod
    def _format_point(x: list[float] | None, names: list[str]) -> str:
        if x is None:
            return "—"
        return ", ".join(f"{name}={_fmt(value)}" for name, value in zip(names, x, strict=True))

    @staticmethod
    def _format_solution(
        names: list[str], x: list[float], obj_value: float, is_max: bool
    ) -> str:
        sense_text = "Maximización" if is_max else "Minimización"
        output = f"""**Solución Entera Óptima Encontrada ✅**

**Tipo:** {sense_text}
**Valor Óptimo:** {obj_value:.4f}

**Valores de las Variables:**
"""
        for name, value in zip(names, x, strict=True):
            display_val = value if abs(value) > 1e-8 else 0.0
            output += f"- {name} = {round(display_val):.0f}\n"
        output += "\n*El árbol anterior fue calculado, no estimado.*"
        return output

    @staticmethod
    def _format_infeasible() -> str:
        return """**Problema Infactible** ❌

No existe ninguna solución entera factible: todos los nodos del árbol resultaron
infactibles o fueron podados sin encontrar una solución entera.

**Posibles causas:**
- Restricciones contradictorias
- Cotas de variables incompatibles con la integralidad
- Error en la formulación del modelo"""

    @staticmethod
    def _format_unbounded(is_max: bool) -> str:
        sense_text = "maximizar" if is_max else "minimizar"
        return f"""**Problema No Acotado** ⚠️

La relajación LP puede {sense_text} indefinidamente, por lo que el problema
entero tampoco está acotado.

**Sugerencia:** Verifica que todas las restricciones necesarias estén incluidas."""

    @staticmethod
    def _format_error(message: str) -> str:
        return f"""**Error** ❌

{message}

Por favor verifica la entrada y vuelve a intentar."""

    async def _arun(self, model_json: str) -> str:
        """Async version - just calls sync version."""
        return self._run(model_json)
