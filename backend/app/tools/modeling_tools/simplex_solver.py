"""
Simplex Solver Tool for step-by-step Linear Programming.

Unlike 'ProblemSolverTool' (which calls scipy and returns only the final
optimum), this tool runs an explicit tableau-based **two-phase Simplex** and
returns every iteration: Phase I and Phase II tableaus, the entering/leaving
variables, the min-ratio test, and the pivot element. The pedagogical goal is
that the agent *explains* verified steps instead of inventing tableaus.
"""

import json
import logging
from typing import Any, ClassVar

from langchain_core.tools import BaseTool

from ._lp_parsing import (
    parse_constraint_expression,
    parse_objective_coefficients,
    parse_variables,
)

logger = logging.getLogger(__name__)

# Try to import numpy - gracefully handle if not installed
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None
    logger.warning(
        "numpy not installed - SimplexSolverTool will have limited functionality"
    )


def _fmt(value: float) -> str:
    """Format a tableau number compactly, snapping tiny values to 0."""
    if abs(value) < 1e-9:
        return "0"
    return f"{value:.4g}"


class SimplexSolverTool(BaseTool):
    """
    Tool for solving small LP problems step by step with the two-phase Simplex.

    Handles ``<=``, ``>=`` and ``=`` constraints (Phase I introduces artificial
    variables when needed). Variables are assumed non-negative (``x >= 0``).
    Integer/binary types are treated as continuous — this is the LP relaxation.
    """

    name: str = "simplex_solver"
    description: str = """Resuelve un problema de Programación Lineal PASO A PASO con el método símplex de dos fases (máximo 20 variables).

Úsalo cuando el estudiante pida ver el método símplex, los tableaus, las iteraciones, el pivoteo, o resolver "paso a paso". Para sólo el óptimo final usa problem_solver.

Entrada: JSON con la misma estructura que problem_solver:
{
  "variables": [
    {"name": "x1", "lower": 0},
    {"name": "x2", "lower": 0}
  ],
  "objective": {
    "sense": "maximize",
    "expression": "3*x1 + 5*x2"
  },
  "constraints": [
    {"expression": "x1 + 2*x2 <= 10", "name": "r1"},
    {"expression": "x1 + x2 >= 3", "name": "r2"}
  ]
}

Retorna: cada iteración (tableau, variable entrante, variable saliente, prueba del cociente mínimo, elemento pivote) en Fase I y Fase II, y la solución óptima.
Estados posibles: óptimo, infactible (Infactible), no acotado (No Acotado), error."""

    model_config = {"arbitrary_types_allowed": True}

    MAX_VARIABLES: ClassVar[int] = 20
    MAX_CONSTRAINTS: ClassVar[int] = 50
    MAX_ITERATIONS: ClassVar[int] = 50
    EPS: ClassVar[float] = 1e-9

    def _run(self, model_json: str) -> str:
        """Solve the LP step by step and return a Markdown report."""
        if not NUMPY_AVAILABLE:
            return self._format_error(
                "numpy no está instalado. Instale con: pip install numpy"
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
            names, _types, bounds = parse_variables(variables)
            obj_coeffs, is_max = parse_objective_coefficients(objective, names)

            for lb, _ub in bounds:
                if lb is not None and lb < 0:
                    return self._format_error(
                        "El método símplex de esta herramienta asume variables "
                        "no negativas (x >= 0). Reformula sin cotas inferiores "
                        "negativas."
                    )

            standard = self._build_standard_form(constraints, names, bounds)
            return self._solve(standard, names, obj_coeffs, is_max)

        except ValueError as e:
            return self._format_error(f"Error en la formulación: {str(e)}")
        except Exception as e:
            logger.exception("Error solving LP with simplex")
            return self._format_error(f"Error al resolver: {str(e)}")

    # ------------------------------------------------------------------ #
    # Standard form construction
    # ------------------------------------------------------------------ #
    def _build_standard_form(
        self,
        constraints: list[dict[str, Any]],
        names: list[str],
        bounds: list[tuple[float | None, float | None]],
    ) -> dict[str, Any]:
        """
        Build the simplex standard form (slack/surplus/artificial columns).

        Returns a dict with the tableau matrix ``A``, RHS ``b``, the initial
        ``basis``, column names/labels, and the set of artificial columns.
        """
        n_dec = len(names)

        # (coeffs over decision vars, rhs, sense)
        rows: list[tuple[list[float], float, str]] = []

        for i, constraint in enumerate(constraints):
            expression = constraint.get("expression", "")
            cname = constraint.get("name", f"r{i + 1}")
            if not expression:
                raise ValueError(f"Restricción '{cname}' vacía")
            lhs, rhs, sense = parse_constraint_expression(expression, names)
            rows.append((lhs, rhs, sense))

        # Encode non-default variable bounds as extra constraints.
        for j, (lb, ub) in enumerate(bounds):
            unit = [0.0] * n_dec
            unit[j] = 1.0
            if lb is not None and lb > self.EPS:
                rows.append((list(unit), float(lb), ">="))
            if ub is not None:
                rows.append((list(unit), float(ub), "<="))

        # Normalize each row so RHS >= 0 (flip sense when multiplying by -1).
        flip = {"<=": ">=", ">=": "<=", "=": "="}
        norm_rows: list[tuple[list[float], float, str]] = []
        for lhs, rhs, sense in rows:
            if rhs < 0:
                lhs = [-c for c in lhs]
                rhs = -rhs
                sense = flip[sense]
            norm_rows.append((lhs, rhs, sense))

        m = len(norm_rows)

        # Assign slack / surplus / artificial columns.
        slack_names: list[str] = []
        surplus_names: list[str] = []
        art_names: list[str] = []
        row_slack: list[int | None] = [None] * m
        row_surplus: list[int | None] = [None] * m
        row_art: list[int | None] = [None] * m

        for i, (_lhs, _rhs, sense) in enumerate(norm_rows):
            if sense == "<=":
                row_slack[i] = len(slack_names)
                slack_names.append(f"s{len(slack_names) + 1}")
            elif sense == ">=":
                row_surplus[i] = len(surplus_names)
                surplus_names.append(f"e{len(surplus_names) + 1}")
                row_art[i] = len(art_names)
                art_names.append(f"a{len(art_names) + 1}")
            elif sense == "=":
                row_art[i] = len(art_names)
                art_names.append(f"a{len(art_names) + 1}")

        n_slack = len(slack_names)
        n_surp = len(surplus_names)
        n_art = len(art_names)
        col_names = list(names) + slack_names + surplus_names + art_names
        total = len(col_names)

        slack_off = n_dec
        surp_off = n_dec + n_slack
        art_off = n_dec + n_slack + n_surp

        a_mat = np.zeros((m, total))
        b_vec = np.zeros(m)
        basis: list[int] = [0] * m

        for i, (lhs, rhs, sense) in enumerate(norm_rows):
            for j in range(n_dec):
                a_mat[i, j] = lhs[j]
            b_vec[i] = rhs
            if sense == "<=":
                ci = slack_off + row_slack[i]
                a_mat[i, ci] = 1.0
                basis[i] = ci
            elif sense == ">=":
                a_mat[i, surp_off + row_surplus[i]] = -1.0
                ca = art_off + row_art[i]
                a_mat[i, ca] = 1.0
                basis[i] = ca
            elif sense == "=":
                ca = art_off + row_art[i]
                a_mat[i, ca] = 1.0
                basis[i] = ca

        artificial_cols = set(range(art_off, art_off + n_art))

        return {
            "A": a_mat,
            "b": b_vec,
            "basis": basis,
            "col_names": col_names,
            "n_dec": n_dec,
            "artificial_cols": artificial_cols,
        }

    # ------------------------------------------------------------------ #
    # Simplex engine
    # ------------------------------------------------------------------ #
    def _solve(
        self,
        standard: dict[str, Any],
        names: list[str],
        obj_coeffs: list[float],
        is_max: bool,
    ) -> str:
        a_mat = standard["A"]
        b_vec = standard["b"]
        basis = standard["basis"]
        col_names = standard["col_names"]
        n_dec = standard["n_dec"]
        artificial_cols = standard["artificial_cols"]
        total = len(col_names)

        steps: list[dict[str, Any]] = []

        # --- Phase I: minimize sum of artificial variables (if any) --- #
        # ``cost`` drives the engine (always minimization); ``display_cost``
        # drives the printed tableau in the problem's natural sense.
        if artificial_cols:
            c1 = np.zeros(total)
            for j in artificial_cols:
                c1[j] = 1.0
            status1 = self._run_simplex(
                a_mat, b_vec, basis, c1, c1, True, set(), col_names, steps, "Fase I"
            )
            if status1 == "max_iter":
                return self._format_cycling()
            phase1_obj = c1[np.array(basis)] @ b_vec
            if phase1_obj > 1e-6:
                return self._format_infeasible()
            # Drive any artificial still basic (at value ~0) out of the basis.
            self._drive_out_artificials(a_mat, b_vec, basis, artificial_cols)
            # Drop artificial columns for Phase II (textbook practice). They are
            # the last columns, so non-artificial indices are unchanged. Only
            # drop if none remains basic (a redundant row could keep one at ~0).
            if not any(col in artificial_cols for col in basis):
                art_off = min(artificial_cols)
                a_mat = a_mat[:, :art_off]
                col_names = col_names[:art_off]
                total = art_off
                artificial_cols = set()

        # --- Phase II: optimize the real objective --- #
        display_cost = np.zeros(total)
        for j in range(n_dec):
            display_cost[j] = obj_coeffs[j]
        # Engine minimizes internally; negate the objective for maximization.
        c2 = -display_cost if is_max else display_cost.copy()

        status2 = self._run_simplex(
            a_mat,
            b_vec,
            basis,
            c2,
            display_cost,
            not is_max,  # pick most negative cj-zj only when minimizing
            set(artificial_cols),
            col_names,
            steps,
            "Fase II",
        )
        if status2 == "unbounded":
            return self._format_steps(steps, names, n_dec) + "\n\n" + (
                self._format_unbounded(is_max)
            )
        if status2 == "max_iter":
            return self._format_cycling()

        # --- Extract optimal solution --- #
        x = [0.0] * n_dec
        for i, col in enumerate(basis):
            if col < n_dec:
                x[col] = float(b_vec[i])
        obj_value = sum(obj_coeffs[j] * x[j] for j in range(n_dec))

        report = self._format_steps(steps, names, n_dec)
        report += "\n\n" + self._format_solution(names, x, obj_value, is_max)
        return report

    def _run_simplex(
        self,
        a_mat: "np.ndarray",
        b_vec: "np.ndarray",
        basis: list[int],
        cost: "np.ndarray",
        display_cost: "np.ndarray",
        pick_most_negative: bool,
        forbidden: set[int],
        col_names: list[str],
        steps: list[dict[str, Any]],
        phase: str,
    ) -> str:
        """
        Run a primal simplex in place, recording each iteration.

        'cost' always drives the engine in minimization form (entering =
        most negative internal reduced cost). 'display_cost' is used only to
        render the tableau in the problem's natural sense; 'pick_most_negative'
        flags how the printed ``cj - zj`` row should be read (most negative when
        minimizing, most positive when maximizing). The selected pivot is
        identical either way since internal reduced = -display reduced.

        Returns "optimal", "unbounded" or "max_iter".
        """
        m, total = a_mat.shape

        for iteration in range(1, self.MAX_ITERATIONS + 1):
            cb = cost[np.array(basis)]
            internal_reduced = cost - cb @ a_mat

            cb_disp = display_cost[np.array(basis)]
            display_reduced = display_cost - cb_disp @ a_mat  # c_j - z_j (shown)
            display_obj = float(cb_disp @ b_vec)

            # Entering: most negative internal reduced cost among allowed,
            # non-basic cols. Equivalent to the most positive cj-zj when maximizing.
            entering = -1
            best = -self.EPS
            for j in range(total):
                if j in forbidden or j in basis:
                    continue
                if internal_reduced[j] < best:
                    best = internal_reduced[j]
                    entering = j

            snapshot: dict[str, Any] = {
                "phase": phase,
                "iteration": iteration,
                "basis": list(basis),
                "col_names": col_names,
                "A": a_mat.copy(),
                "b": b_vec.copy(),
                "reduced": display_reduced.copy(),
                "obj": display_obj,
                "pick_most_negative": pick_most_negative,
                "entering": None,
                "leaving_row": None,
                "leaving_col": None,
                "pivot": None,
                "ratios": [],
                "status": None,
            }

            if entering == -1:
                snapshot["status"] = "optimal"
                steps.append(snapshot)
                return "optimal"

            # Min-ratio test for the leaving variable.
            ratios: list[tuple[int, float]] = []
            leaving_row = -1
            min_ratio = float("inf")
            for i in range(m):
                aij = a_mat[i, entering]
                if aij > self.EPS:
                    ratio = b_vec[i] / aij
                    ratios.append((i, ratio))
                    # Bland-style tie-break: prefer smaller basis column index.
                    if ratio < min_ratio - self.EPS or (
                        abs(ratio - min_ratio) <= self.EPS
                        and leaving_row != -1
                        and basis[i] < basis[leaving_row]
                    ):
                        min_ratio = ratio
                        leaving_row = i

            snapshot["entering"] = entering
            snapshot["ratios"] = ratios

            if leaving_row == -1:
                snapshot["status"] = "unbounded"
                steps.append(snapshot)
                return "unbounded"

            snapshot["leaving_row"] = leaving_row
            snapshot["leaving_col"] = basis[leaving_row]
            snapshot["pivot"] = float(a_mat[leaving_row, entering])
            steps.append(snapshot)

            self._pivot(a_mat, b_vec, leaving_row, entering)
            basis[leaving_row] = entering

        return "max_iter"

    @staticmethod
    def _pivot(
        a_mat: "np.ndarray", b_vec: "np.ndarray", row: int, col: int
    ) -> None:
        """Gauss-Jordan pivot on (row, col), updating A and b in place."""
        pivot_val = a_mat[row, col]
        a_mat[row, :] /= pivot_val
        b_vec[row] /= pivot_val
        m = a_mat.shape[0]
        for i in range(m):
            if i == row:
                continue
            factor = a_mat[i, col]
            if factor != 0.0:
                a_mat[i, :] -= factor * a_mat[row, :]
                b_vec[i] -= factor * b_vec[row]

    def _drive_out_artificials(
        self,
        a_mat: "np.ndarray",
        b_vec: "np.ndarray",
        basis: list[int],
        artificial_cols: set[int],
    ) -> None:
        """Pivot artificial variables left in the basis (at value ~0) out."""
        m, total = a_mat.shape
        for i in range(m):
            if basis[i] in artificial_cols:
                for j in range(total):
                    if j in artificial_cols or j in basis:
                        continue
                    if abs(a_mat[i, j]) > self.EPS:
                        self._pivot(a_mat, b_vec, i, j)
                        basis[i] = j
                        break

    # ------------------------------------------------------------------ #
    # Formatting
    # ------------------------------------------------------------------ #
    def _format_steps(
        self, steps: list[dict[str, Any]], names: list[str], n_dec: int
    ) -> str:
        parts: list[str] = ["**Método Símplex paso a paso** 🧮"]
        current_phase: str | None = None
        for step in steps:
            if step["phase"] != current_phase:
                current_phase = step["phase"]
                if current_phase == "Fase I":
                    parts.append(
                        f"\n## {current_phase}: minimizar la suma de variables "
                        "artificiales (buscar una solución factible)"
                    )
                else:
                    parts.append(
                        f"\n## {current_phase}: optimizar la función objetivo real"
                    )
            parts.append(self._format_tableau(step, names))
        return "\n".join(parts)

    @staticmethod
    def _format_tableau(step: dict[str, Any], names: list[str]) -> str:
        col_names = step["col_names"]
        basis = step["basis"]
        a_mat = step["A"]
        b_vec = step["b"]
        reduced = step["reduced"]
        m = a_mat.shape[0]

        lines: list[str] = [f"\n### {step['phase']} — Iteración {step['iteration']}"]

        # Header
        header = "| Base | " + " | ".join(col_names) + " | LD |"
        sep = "|" + "---|" * (len(col_names) + 2)
        lines.append(header)
        lines.append(sep)

        for i in range(m):
            base_label = col_names[basis[i]]
            coeffs = " | ".join(_fmt(a_mat[i, j]) for j in range(len(col_names)))
            lines.append(f"| {base_label} | {coeffs} | {_fmt(b_vec[i])} |")

        # Reduced-cost row (c_j - z_j), objective value in the RHS cell.
        reduced_cells = " | ".join(_fmt(reduced[j]) for j in range(len(col_names)))
        lines.append(f"| cj - zj | {reduced_cells} | z = {_fmt(step['obj'])} |")

        # Annotations
        pick_neg = step.get("pick_most_negative", True)
        if step["status"] == "optimal":
            cond = "≥ 0" if pick_neg else "≤ 0"
            lines.append(
                f"\n✅ **Óptimo de la fase**: todos los `cj - zj` {cond}, "
                "no hay variable entrante."
            )
            return "\n".join(lines)

        if step["status"] == "unbounded":
            entering_name = col_names[step["entering"]]
            lines.append(
                f"\n⚠️ La variable entrante **{entering_name}** no tiene ningún "
                "cociente positivo en la prueba del cociente mínimo → problema "
                "**No Acotado**."
            )
            return "\n".join(lines)

        entering_name = col_names[step["entering"]]
        leaving_name = col_names[step["leaving_col"]]
        extreme = "el más negativo" if pick_neg else "el más positivo"
        lines.append(
            f"\n- **Variable entrante:** `{entering_name}` "
            f"(`cj - zj` = {_fmt(reduced[step['entering']])}, {extreme})"
        )
        # Min-ratio test detail
        ratio_strs = []
        for i, ratio in step["ratios"]:
            mark = " ← mínimo" if i == step["leaving_row"] else ""
            ratio_strs.append(
                f"{col_names[basis[i]]}: {_fmt(b_vec[i])} / "
                f"{_fmt(a_mat[i, step['entering']])} = {_fmt(ratio)}{mark}"
            )
        lines.append(
            "- **Prueba del cociente mínimo:** " + "; ".join(ratio_strs)
        )
        lines.append(
            f"- **Variable saliente:** `{leaving_name}` | "
            f"**Elemento pivote:** {_fmt(step['pivot'])}"
        )
        return "\n".join(lines)

    @staticmethod
    def _format_solution(
        names: list[str], x: list[float], obj_value: float, is_max: bool
    ) -> str:
        sense_text = "Maximización" if is_max else "Minimización"
        output = f"""## Solución Óptima Encontrada ✅

**Tipo:** {sense_text}
**Valor Óptimo:** {obj_value:.4f}

**Valores de las Variables:**
"""
        for name, value in zip(names, x, strict=True):
            display_val = value if abs(value) > 1e-8 else 0.0
            output += f"- {name} = {display_val:.4f}\n"
        output += "\n*Los tableaus anteriores fueron calculados, no estimados.*"
        return output

    @staticmethod
    def _format_infeasible() -> str:
        return """**Problema Infactible** ❌

La Fase I terminó con variables artificiales en valor positivo: no existe
solución factible que satisfaga todas las restricciones simultáneamente.

**Posibles causas:**
- Restricciones contradictorias
- Cotas de variables incompatibles
- Error en la formulación del modelo"""

    @staticmethod
    def _format_unbounded(is_max: bool) -> str:
        sense_text = "maximizar" if is_max else "minimizar"
        return f"""**Problema No Acotado** ⚠️

La función objetivo puede {sense_text} indefinidamente: la columna de la
variable entrante no tiene ningún cociente positivo en la prueba del cociente
mínimo.

**Sugerencia:** Verifica que todas las restricciones necesarias estén incluidas."""

    @staticmethod
    def _format_cycling() -> str:
        return """**No se alcanzó el óptimo** ⚠️

El método símplex superó el número máximo de iteraciones (posible ciclado o
degeneración). Revisa la formulación o usa problem_solver para el óptimo final."""

    @staticmethod
    def _format_error(message: str) -> str:
        return f"""**Error** ❌

{message}

Por favor verifica la entrada y vuelve a intentar."""

    async def _arun(self, model_json: str) -> str:
        """Async version - just calls sync version."""
        return self._run(model_json)
