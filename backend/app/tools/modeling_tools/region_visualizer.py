"""
Region Visualizer Tool for Mathematical Modeling.

This tool generates 2D plots of feasible regions for LP problems
with 2 variables.
"""

import base64
import io
import json
import logging
from typing import Any, ClassVar

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# Try to import visualization libraries
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon # noqa: F401
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None
    plt = None
    logger.warning("matplotlib not installed - RegionVisualizerTool will have limited functionality")


class RegionVisualizerTool(BaseTool):
    """
    Tool for visualizing 2D feasible regions of LP problems.

    Creates plots showing:
    - Constraint lines
    - Feasible region (shaded)
    - Corner points (vertices)
    - Optional objective function direction
    """

    name: str = "region_visualizer"
    description: str = """Crea una visualización 2D de la región factible para problemas LP con 2 variables.

Entrada: JSON con la siguiente estructura:
{
  "variables": [
    {"name": "x1", "lower": 0},
    {"name": "x2", "lower": 0}
  ],
  "constraints": [
    {"expression": "x1 + 2*x2 <= 10", "name": "recurso1"},
    {"expression": "2*x1 + x2 <= 8", "name": "recurso2"}
  ],
  "objective": {
    "sense": "maximize",
    "expression": "3*x1 + 5*x2"
  }
}

IMPORTANTE: Solo funciona con exactamente 2 variables.

Retorna: Imagen PNG codificada en base64 de la región factible."""

    model_config = {"arbitrary_types_allowed": True}

    # Plot settings
    FIGURE_SIZE: ClassVar[tuple[int, int]] = (8, 6)
    DPI: ClassVar[int] = 100
    COLORS: ClassVar[list[str]] = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#a65628']

    def _run(self, model_json: str) -> str:
        """
        Generate the feasible region plot.

        Args:
            model_json: JSON string with model specification

        Returns:
            Base64 encoded PNG image or error message
        """
        if not NUMPY_AVAILABLE or not MATPLOTLIB_AVAILABLE:
            missing = []
            if not NUMPY_AVAILABLE:
                missing.append("numpy")
            if not MATPLOTLIB_AVAILABLE:
                missing.append("matplotlib")
            return self._format_error(
                f"Librerías no instaladas: {', '.join(missing)}. "
                f"Instale con: pip install {' '.join(missing)}"
            )

        # Parse JSON
        try:
            model = json.loads(model_json)
        except json.JSONDecodeError as e:
            return self._format_error(f"Error al parsear JSON: {str(e)}")

        # Extract components
        variables = model.get("variables", [])
        constraints = model.get("constraints", [])
        objective = model.get("objective", {})

        # Validate 2 variables
        if len(variables) != 2:
            return self._format_error(
                f"Esta herramienta solo funciona con 2 variables. "
                f"Se proporcionaron {len(variables)} variables."
            )

        if not constraints:
            return self._format_error("No se proporcionaron restricciones")

        try:
            var_names = [v.get("name", f"x{i+1}") for i, v in enumerate(variables)]
            var_bounds = self._get_variable_bounds(variables)

            # Parse constraints
            parsed_constraints = self._parse_constraints(constraints, var_names)

            # Generate the plot
            image_base64 = self._generate_plot(
                var_names=var_names,
                var_bounds=var_bounds,
                constraints=parsed_constraints,
                objective=objective
            )

            return f"""**Visualización de Región Factible** ✅

La imagen muestra:
- **Líneas de restricción** en diferentes colores
- **Región factible** sombreada en azul claro
- **Puntos esquina** (vértices) marcados en rojo
- **Ejes** etiquetados con los nombres de las variables

![Región Factible](data:image/png;base64,{image_base64})

*Nota: Los puntos esquina son las soluciones candidatas a óptimo en programación lineal.*"""

        except ValueError as e:
            return self._format_error(f"Error en la formulación: {str(e)}")
        except Exception as e:
            logger.exception("Error generating feasible region plot")
            return self._format_error(f"Error al generar gráfico: {str(e)}")

    @staticmethod
    def _get_variable_bounds(
            variables: list[dict[str, Any]]
    ) -> list[tuple[float, float]]:
        """Get bounds for each variable."""
        bounds = []
        for var in variables:
            lower = var.get("lower", 0)
            upper = var.get("upper")
            if lower is None:
                lower = 0
            if upper is None:
                upper = float('inf')
            bounds.append((float(lower), float(upper)))
        return bounds

    def _parse_constraints(
        self, constraints: list[dict[str, Any]], var_names: list[str]
    ) -> list[dict[str, Any]]:
        """Parse constraints into coefficient form."""
        parsed = []

        for constraint in constraints:
            name = constraint.get("name", f"c{len(parsed)+1}")
            expression = constraint.get("expression", "")

            if not expression:
                continue

            # Find operator
            for op in ["<=", ">=", "="]:
                if op in expression:
                    parts = expression.split(op, 1)
                    if len(parts) == 2:
                        lhs, rhs = parts[0].strip(), parts[1].strip()
                        coeffs = self._parse_expression(lhs, var_names)
                        try:
                            rhs_val = float(rhs)
                        except ValueError:
                            rhs_val = 0

                        parsed.append({
                            "name": name,
                            "coeffs": coeffs,
                            "rhs": rhs_val,
                            "sense": op
                        })
                        break

        return parsed

    @staticmethod
    def _parse_expression(
            expression: str, var_names: list[str]
    ) -> list[float]:
        """Parse a linear expression into coefficients."""
        coefficients = [0.0, 0.0]

        expr = expression.replace(" ", "").replace("-", "+-")
        terms = [t for t in expr.split("+") if t]

        for term in terms:
            for i, var in enumerate(var_names):
                if var in term:
                    coef_str = term.replace(var, "").replace("*", "").strip()
                    if not coef_str or coef_str == "+":
                        coef = 1.0
                    elif coef_str == "-":
                        coef = -1.0
                    else:
                        try:
                            coef = float(coef_str)
                        except ValueError:
                            coef = 1.0
                    coefficients[i] += coef
                    break

        return coefficients

    def _generate_plot(
        self,
        var_names: list[str],
        var_bounds: list[tuple[float, float]],
        constraints: list[dict[str, Any]],
        objective: dict[str, Any]
    ) -> str:
        """Generate the feasible region plot."""
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZE, dpi=self.DPI)

        # Determine plot bounds
        x_max, y_max = self._calculate_plot_bounds(constraints, var_bounds)

        # Create a fine grid for shading
        x = np.linspace(0, x_max, 500)
        y = np.linspace(0, y_max, 500)
        X, Y = np.meshgrid(x, y)

        # Start with a feasible region as all True
        feasible = np.ones_like(X, dtype=bool)

        # Apply variable bounds
        if var_bounds[0][0] is not None:
            feasible &= (X >= var_bounds[0][0])
        if var_bounds[0][1] != float('inf'):
            feasible &= (X <= var_bounds[0][1])
        if var_bounds[1][0] is not None:
            feasible &= (Y >= var_bounds[1][0])
        if var_bounds[1][1] != float('inf'):
            feasible &= (Y <= var_bounds[1][1])

        # Apply each constraint
        for constraint in constraints:
            a, b = constraint["coeffs"]
            rhs = constraint["rhs"]
            sense = constraint["sense"]

            if sense == "<=":
                feasible &= (a * X + b * Y <= rhs + 1e-10)
            elif sense == ">=":
                feasible &= (a * X + b * Y >= rhs - 1e-10)
            elif sense == "=":
                feasible &= np.abs(a * X + b * Y - rhs) < 0.1

        # Shade feasible region
        ax.contourf(X, Y, feasible.astype(int), levels=[0.5, 1.5],
                    colors=['#a6cee3'], alpha=0.5)
        ax.contour(X, Y, feasible.astype(int), levels=[0.5],
                   colors=['#1f78b4'], linewidths=2)

        # Plot constraint lines
        for i, constraint in enumerate(constraints):
            a, b = constraint["coeffs"]
            rhs = constraint["rhs"]
            name = constraint["name"]
            color = self.COLORS[i % len(self.COLORS)]

            if abs(b) > 1e-10:
                # y = (rhs - a*x) / b
                x_line = np.linspace(0, x_max, 100)
                y_line = (rhs - a * x_line) / b
                # Clip to visible range
                mask = (y_line >= -0.5) & (y_line <= y_max + 0.5)
                if np.any(mask):
                    ax.plot(x_line[mask], y_line[mask], color=color,
                           linewidth=2, label=f"{name}: {self._format_constraint(constraint)}")
            elif abs(a) > 1e-10:
                # Vertical line: x = rhs/a
                x_val = rhs / a
                if 0 <= x_val <= x_max:
                    ax.axvline(x=x_val, color=color, linewidth=2,
                              label=f"{name}: {self._format_constraint(constraint)}")

        # Find and plot corner points
        corners = self._find_corner_points(constraints, var_bounds, x_max, y_max)
        if corners:
            corners_x = [c[0] for c in corners]
            corners_y = [c[1] for c in corners]
            ax.scatter(corners_x, corners_y, color='red', s=100, zorder=5,
                      edgecolors='darkred', linewidths=2, label='Vértices')

            # Label corner points
            for cx, cy in corners:
                ax.annotate(f'({cx:.1f}, {cy:.1f})',
                           (cx, cy), textcoords="offset points",
                           xytext=(5, 5), fontsize=9,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

        # Plot objective function direction if provided
        if objective and objective.get("expression"):
            self._add_objective_arrow(ax, objective, var_names, x_max, y_max)

        # Formatting
        ax.set_xlim(-0.5, x_max + 0.5)
        ax.set_ylim(-0.5, y_max + 0.5)
        ax.set_xlabel(var_names[0], fontsize=12)
        ax.set_ylabel(var_names[1], fontsize=12)
        ax.set_title('Región Factible', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=9)
        ax.set_aspect('equal', adjustable='box')

        # Add non-negativity indicators
        ax.axhline(color='black', linewidth=1)
        ax.axvline(color='black', linewidth=1)

        plt.tight_layout()

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=self.DPI, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)

        return image_base64

    @staticmethod
    def _calculate_plot_bounds(
            constraints: list[dict[str, Any]],
        var_bounds: list[tuple[float, float]]
    ) -> tuple[float, float]:
        """Calculate appropriate plot bounds."""
        x_max = 10.0
        y_max = 10.0

        # Check variable upper bounds
        if var_bounds[0][1] != float('inf'):
            x_max = max(x_max, var_bounds[0][1] * 1.2)
        if var_bounds[1][1] != float('inf'):
            y_max = max(y_max, var_bounds[1][1] * 1.2)

        # Check constraint intercepts
        for constraint in constraints:
            a, b = constraint["coeffs"]
            rhs = constraint["rhs"]

            if abs(a) > 1e-10:
                x_intercept = rhs / a
                if x_intercept > 0:
                    x_max = max(x_max, x_intercept * 1.2)

            if abs(b) > 1e-10:
                y_intercept = rhs / b
                if y_intercept > 0:
                    y_max = max(y_max, y_intercept * 1.2)

        # Cap at reasonable values
        x_max = min(x_max, 100)
        y_max = min(y_max, 100)

        return x_max, y_max

    def _find_corner_points(
        self,
        constraints: list[dict[str, Any]],
        var_bounds: list[tuple[float, float]],
        x_max: float,
        y_max: float
    ) -> list[tuple[float, float]]:
        """Find corner points of the feasible region."""
        corners = []

        # Add boundary constraints as implicit constraints
        all_constraints = constraints.copy()

        # x >= lower_x (if specified)
        if var_bounds[0][0] is not None:
            all_constraints.append({"coeffs": [1, 0], "rhs": var_bounds[0][0], "sense": ">="})
        # y >= lower_y (if specified)
        if var_bounds[1][0] is not None:
            all_constraints.append({"coeffs": [0, 1], "rhs": var_bounds[1][0], "sense": ">="})

        # Find intersections of all pairs of constraints
        for i in range(len(all_constraints)):
            for j in range(i + 1, len(all_constraints)):
                point = self._intersect_lines(all_constraints[i], all_constraints[j])
                if point is not None:
                    x, y = point
                    # Check if the point is feasible
                    if self._is_feasible(x, y, constraints, var_bounds):
                        # Check if not already added (with tolerance)
                        is_duplicate = any(
                            abs(x - cx) < 1e-6 and abs(y - cy) < 1e-6
                            for cx, cy in corners
                        )
                        if not is_duplicate and 0 <= x <= x_max + 1 and 0 <= y <= y_max + 1:
                            corners.append((round(x, 4), round(y, 4)))

        return corners

    @staticmethod
    def _intersect_lines(
            c1: dict[str, Any],
        c2: dict[str, Any]
    ) -> tuple[float, float] | None:
        """Find the intersection of two constraint lines."""
        a1, b1 = c1["coeffs"]
        r1 = c1["rhs"]
        a2, b2 = c2["coeffs"]
        r2 = c2["rhs"]

        det = a1 * b2 - a2 * b1

        if abs(det) < 1e-10:
            return None  # Parallel lines

        x = (r1 * b2 - r2 * b1) / det
        y = (a1 * r2 - a2 * r1) / det

        return x, y

    @staticmethod
    def _is_feasible(
            x: float,
        y: float,
        constraints: list[dict[str, Any]],
        var_bounds: list[tuple[float, float]]
    ) -> bool:
        """Check if a point is feasible."""
        # Check bounds
        if x < var_bounds[0][0] - 1e-6:
            return False
        if var_bounds[0][1] != float('inf') and x > var_bounds[0][1] + 1e-6:
            return False
        if y < var_bounds[1][0] - 1e-6:
            return False
        if var_bounds[1][1] != float('inf') and y > var_bounds[1][1] + 1e-6:
            return False

        # Check constraints
        for constraint in constraints:
            a, b = constraint["coeffs"]
            rhs = constraint["rhs"]
            sense = constraint["sense"]
            lhs_val = a * x + b * y

            if sense == "<=" and lhs_val > rhs + 1e-6:
                return False
            if sense == ">=" and lhs_val < rhs - 1e-6:
                return False
            if sense == "=" and abs(lhs_val - rhs) > 1e-6:
                return False

        return True

    def _add_objective_arrow(
        self,
        ax,
        objective: dict[str, Any],
        var_names: list[str],
        x_max: float,
        y_max: float
    ):
        """Add an arrow showing an objective function direction."""
        expression = objective.get("expression", "")
        sense = objective.get("sense", "maximize").lower()

        coeffs = self._parse_expression(expression, var_names)

        if abs(coeffs[0]) < 1e-10 and abs(coeffs[1]) < 1e-10:
            return

        # Normalize the gradient vector
        norm = np.sqrt(coeffs[0]**2 + coeffs[1]**2)
        dx = coeffs[0] / norm
        dy = coeffs[1] / norm

        # For minimization, reverse direction
        if sense in ("minimize", "min", "minimizar"):
            dx, dy = -dx, -dy

        # Place an arrow in a corner of the plot
        arrow_start = (x_max * 0.85, y_max * 0.15)
        arrow_scale = min(x_max, y_max) * 0.1

        ax.annotate('',
                   xy=(arrow_start[0] + dx * arrow_scale,
                       arrow_start[1] + dy * arrow_scale),
                   xytext=arrow_start,
                   arrowprops=dict(arrowstyle='->', color='green', lw=2))

        direction = "mejora" if sense in ("maximize", "max", "maximizar") else "mejora"
        ax.text(arrow_start[0], arrow_start[1] - y_max * 0.05,
               f'Dirección de\n{direction}', fontsize=8, color='green',
               ha='center')

    @staticmethod
    def _format_constraint(constraint: dict[str, Any]) -> str:
        """Format constraint for display in legend."""
        a, b = constraint["coeffs"]
        rhs = constraint["rhs"]
        sense = constraint["sense"]

        parts = []
        if abs(a) > 1e-10:
            if abs(a - 1) < 1e-10:
                parts.append("x₁")
            elif abs(a + 1) < 1e-10:
                parts.append("-x₁")
            else:
                parts.append(f"{a:.1f}x₁")

        if abs(b) > 1e-10:
            if abs(b - 1) < 1e-10:
                parts.append("+ x₂" if parts else "x₂")
            elif abs(b + 1) < 1e-10:
                parts.append("- x₂")
            elif b > 0:
                parts.append(f"+ {b:.1f}x₂" if parts else f"{b:.1f}x₂")
            else:
                parts.append(f"- {abs(b):.1f}x₂")

        lhs = " ".join(parts) if parts else "0"
        return f"{lhs} {sense} {rhs:.1f}"

    @staticmethod
    def _format_error(message: str) -> str:
        """Format an error message."""
        return f"""**Error** ❌

{message}

Esta herramienta visualiza regiones factibles para problemas con **exactamente 2 variables**.
Asegúrese de proporcionar las restricciones en formato correcto."""

    async def _arun(self, model_json: str) -> str:
        """Async version - just calls sync version."""
        return self._run(model_json)
