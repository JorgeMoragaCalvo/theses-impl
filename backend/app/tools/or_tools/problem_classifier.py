"""
Problem Classifier Tool for Operations Research.

This tool helps students identify what type of optimization problem
they have and recommends the appropriate specialized agent.
"""

import logging
from typing import Any

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class ProblemClassifierTool(BaseTool):
    """
    Tool for classifying optimization problems and recommending agents.

    Analyzes problem descriptions to identify:
    - Variable types (continuous, integer, binary)
    - Relationship types (linear, nonlinear)
    - Problem structure

    Then recommends the appropriate specialized agent.
    """

    name: str = "problem_classifier"
    description: str = """Use this tool to help classify a student's optimization problem.
Input: A description of the problem the student is trying to solve.

Returns:
- Problem classification (LP, IP, MIP, NLP, etc.)
- Key characteristics identified
- Recommended specialized agent to use
- Brief explanation of why this classification

Use this when students describe a real-world problem and need guidance on what type it is."""

    model_config = {"arbitrary_types_allowed": True}

    def _run(self, problem_description: str) -> str:
        """
        Classify the problem and recommend an agent.

        Args:
            problem_description: Description of the optimization problem

        Returns:
            Classification results with agent recommendation
        """
        desc_lower = problem_description.lower()

        # Analyze problem characteristics
        characteristics = self._analyze_characteristics(desc_lower)

        # Determine classification
        classification = self._classify_problem(characteristics)

        # Format and return results
        return self._format_classification(classification, characteristics)

    def _analyze_characteristics(self, description: str) -> dict[str, Any]:
        """
        Analyze problem description for key characteristics.

        Args:
            description: Lowercased problem description

        Returns:
            Dictionary of detected characteristics
        """
        return {
            "has_integer_vars": self._check_integer_vars(description),
            "has_binary_vars": self._check_binary_vars(description),
            "has_nonlinear": self._check_nonlinearity(description),
            "has_continuous_vars": self._check_continuous_vars(description),
            "has_network_structure": self._check_network(description),
            "has_uncertainty": self._check_uncertainty(description),
            "detected_keywords": self._extract_keywords(description),
        }

    @staticmethod
    def _check_integer_vars(desc: str) -> bool:
        """Check for integer variable indicators."""
        indicators = [
            # Spanish
            "entero", "enteros", "número entero", "números enteros",
            "unidades", "cantidad de", "cuántos", "cuantos",
            "camiones", "máquinas", "maquinas", "empleados", "trabajadores",
            "paquetes", "cajas", "lotes", "personas", "vehículos", "vehiculos",
            "almacenes", "plantas", "fábricas", "fabricas", "tiendas",
            # English
            "integer", "integers", "whole number", "whole numbers",
            "units", "how many", "number of",
            "trucks", "machines", "employees", "workers",
            "packages", "boxes", "lots", "people", "vehicles",
            "warehouses", "plants", "factories", "stores",
        ]
        return any(ind in desc for ind in indicators)

    @staticmethod
    def _check_binary_vars(desc: str) -> bool:
        """Check for binary/yes-no decision indicators."""
        indicators = [
            # Spanish
            "sí o no", "si o no", "abrir o cerrar", "seleccionar o no",
            "decisión binaria", "decision binaria", "0 o 1", "0-1",
            "activar", "desactivar", "elegir entre", "asignar o no",
            "construir o no", "contratar o no", "comprar o no",
            # English
            "yes or no", "open or close", "select or not",
            "binary decision", "0 or 1", "activate", "deactivate",
            "choose whether", "assign or not", "build or not",
            "hire or not", "buy or not",
        ]
        return any(ind in desc for ind in indicators)

    @staticmethod
    def _check_nonlinearity(desc: str) -> bool:
        """Check for nonlinear relationship indicators."""
        indicators = [
            # Spanish
            "cuadrático", "cuadratico", "al cuadrado", "exponencial",
            "logarítmico", "logaritmico", "no lineal", "no-lineal",
            "producto de variables", "multiplicar variables",
            "raíz", "raiz", "potencia", "curva", "curvo",
            "economía de escala", "economia de escala",
            "rendimientos decrecientes", "costo marginal creciente",
            # English
            "quadratic", "squared", "exponential", "logarithmic",
            "nonlinear", "non-linear", "product of variables",
            "multiply variables", "square root", "power", "curve",
            "economies of scale", "diminishing returns",
            "increasing marginal cost",
        ]
        return any(ind in desc for ind in indicators)

    @staticmethod
    def _check_continuous_vars(desc: str) -> bool:
        """Check for continuous variable indicators."""
        indicators = [
            # Spanish
            "continuo", "continuos", "fracción", "fraccion", "fracciones",
            "porcentaje", "proporción", "proporcion", "cantidad",
            "kilogramos", "litros", "metros", "horas", "toneladas",
            "galones", "pies", "yardas", "peso", "volumen",
            # English
            "continuous", "fraction", "fractions", "percentage",
            "proportion", "amount", "kilograms", "liters", "meters",
            "hours", "tons", "gallons", "feet", "yards", "weight", "volume",
        ]
        return any(ind in desc for ind in indicators)

    @staticmethod
    def _check_network(desc: str) -> bool:
        """Check for network/graph structure indicators."""
        indicators = [
            # Spanish
            "red", "redes", "nodos", "arcos", "flujo", "ruta",
            "camino más corto", "transporte", "distribución",
            "origen", "destino", "conexiones",
            # English
            "network", "nodes", "arcs", "flow", "route", "path",
            "shortest path", "transportation", "distribution",
            "origin", "destination", "connections",
        ]
        return any(ind in desc for ind in indicators)

    @staticmethod
    def _check_uncertainty(desc: str) -> bool:
        """Check for stochastic/uncertainty indicators."""
        indicators = [
            # Spanish
            "incertidumbre", "probabilidad", "aleatorio", "estocástico",
            "estocastico", "escenarios", "riesgo", "demanda incierta",
            "variabilidad", "distribución de probabilidad",
            # English
            "uncertainty", "probability", "random", "stochastic",
            "scenarios", "risk", "uncertain demand", "variability",
            "probability distribution",
        ]
        return any(ind in desc for ind in indicators)

    @staticmethod
    def _extract_keywords(desc: str) -> list[str]:
        """Extract relevant OR keywords found in the description."""
        keyword_map = {
            # Problem types
            "maximizar": "maximización",
            "maximize": "maximización",
            "minimizar": "minimización",
            "minimize": "minimización",
            "optimizar": "optimización",
            "optimize": "optimización",
            # Constraints
            "restricción": "restricciones",
            "constraint": "restricciones",
            "límite": "límites",
            "limit": "límites",
            "capacidad": "capacidad",
            "capacity": "capacidad",
            "presupuesto": "presupuesto",
            "budget": "presupuesto",
            # Objectives
            "costo": "costos",
            "cost": "costos",
            "ganancia": "ganancias",
            "profit": "ganancias",
            "beneficio": "beneficios",
            "benefit": "beneficios",
            "tiempo": "tiempo",
            "time": "tiempo",
        }

        found = []
        for keyword, label in keyword_map.items():
            if keyword in desc and label not in found:
                found.append(label)
        return found

    @staticmethod
    def _classify_problem(characteristics: dict[str, Any]) -> dict[str, str]:
        """
        Determine problem classification based on characteristics.

        Args:
            characteristics: Detected problem characteristics

        Returns:
            Classification with type and recommended agent
        """
        has_nonlinear = characteristics["has_nonlinear"]
        has_integer = characteristics["has_integer_vars"]
        has_binary = characteristics["has_binary_vars"]
        has_continuous = characteristics["has_continuous_vars"]
        has_uncertainty = characteristics["has_uncertainty"]

        # Classification logic
        if has_nonlinear:
            return {
                "type": "NLP",
                "full_name": "Programación No Lineal (Nonlinear Programming)",
                "agent": "Agente de Programación No Lineal",
                "agent_type": "nonlinear_programming",
                "reason": "Se detectaron relaciones no lineales en el problema",
            }

        if has_binary or has_integer:
            if has_continuous:
                return {
                    "type": "MIP",
                    "full_name": "Programación Entera Mixta (Mixed Integer Programming)",
                    "agent": "Agente de Programación Entera",
                    "agent_type": "integer_programming",
                    "reason": "El problema tiene variables enteras/binarias y continuas",
                }
            if has_binary and not has_integer:
                return {
                    "type": "BIP",
                    "full_name": "Programación Entera Binaria (Binary Integer Programming)",
                    "agent": "Agente de Programación Entera",
                    "agent_type": "integer_programming",
                    "reason": "El problema involucra decisiones de sí/no (variables binarias)",
                }
            return {
                "type": "IP",
                "full_name": "Programación Entera (Integer Programming)",
                "agent": "Agente de Programación Entera",
                "agent_type": "integer_programming",
                "reason": "Las variables de decisión deben ser números enteros",
            }

        # Default to LP if no special characteristics detected
        return {
            "type": "LP",
            "full_name": "Programación Lineal (Linear Programming)",
            "agent": "Agente de Programación Lineal",
            "agent_type": "linear_programming",
            "reason": "Las relaciones son lineales y las variables pueden ser continuas",
        }

    @staticmethod
    def _format_classification(
            classification: dict[str, str], characteristics: dict[str, Any]
    ) -> str:
        """
        Format classification results for display.

        Args:
            classification: Problem classification
            characteristics: Detected characteristics

        Returns:
            Formatted classification string
        """
        result = f"""**Clasificación del Problema**

**Tipo:** {classification['type']} - {classification['full_name']}

**Razón:** {classification['reason']}

**Agente Recomendado:** {classification['agent']}

**Características Detectadas:**"""

        # Add detected characteristics
        char_labels = {
            "has_integer_vars": "Variables enteras",
            "has_binary_vars": "Variables binarias (sí/no)",
            "has_nonlinear": "Relaciones no lineales",
            "has_continuous_vars": "Variables continuas",
            "has_network_structure": "Estructura de red",
            "has_uncertainty": "Incertidumbre/estocástico",
        }

        detected = []
        for key, label in char_labels.items():
            if characteristics.get(key):
                detected.append(f"- {label}")

        if detected:
            result += "\n" + "\n".join(detected)
        else:
            result += "\n- Ninguna característica especial detectada"

        # Add keywords
        keywords = characteristics.get("detected_keywords", [])
        if keywords:
            result += f"\n\n**Conceptos identificados:** {', '.join(keywords)}"

        result += f"""

---
*Para formular y resolver este problema, te recomiendo consultar con el {classification['agent']}.*"""

        return result

    async def _arun(self, problem_description: str) -> str:
        """Async version - just calls sync version since no IO is async."""
        return self._run(problem_description)
