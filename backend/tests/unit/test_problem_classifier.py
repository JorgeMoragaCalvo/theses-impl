"""
Unit tests for ProblemClassifierTool — classification of optimization problems.
"""

from app.tools.or_tools.problem_classifier import ProblemClassifierTool


class TestClassifyLP:
    def setup_method(self):
        self.tool = ProblemClassifierTool()

    def test_basic_lp(self):
        result = self.tool._run(
            "Maximizar la ganancia sujeto a restricciones de capacidad con kilogramos de producto"
        )
        assert "LP" in result or "Lineal" in result

    def test_lp_english(self):
        result = self.tool._run(
            "Maximize profit subject to capacity constraints with hours of labor"
        )
        assert "LP" in result or "Linear" in result


class TestClassifyIP:
    def setup_method(self):
        self.tool = ProblemClassifierTool()

    def test_integer_problem(self):
        result = self.tool._run(
            "Necesito determinar cuántos camiones enviar a cada almacén"
        )
        assert "IP" in result or "Entera" in result

    def test_binary_problem(self):
        result = self.tool._run("Decidir si activar o desactivar cada opción")
        assert "BIP" in result or "Binaria" in result

    def test_mip(self):
        result = self.tool._run(
            "Decidir cuántos camiones enviar y la proporción de cada producto en kilogramos"
        )
        assert "MIP" in result or "Mixta" in result


class TestClassifyNLP:
    def setup_method(self):
        self.tool = ProblemClassifierTool()

    def test_nonlinear(self):
        result = self.tool._run(
            "Minimizar el costo cuadrático de producción con rendimientos decrecientes"
        )
        assert "NLP" in result or "No Lineal" in result


class TestCharacteristics:
    def setup_method(self):
        self.tool = ProblemClassifierTool()

    def test_network_detected(self):
        chars = self.tool._analyze_characteristics(
            "encontrar la ruta más corta entre nodos en una red de distribución"
        )
        assert chars["has_network_structure"] is True

    def test_uncertainty_detected(self):
        chars = self.tool._analyze_characteristics(
            "la demanda es incierta con probabilidad de escenarios"
        )
        assert chars["has_uncertainty"] is True

    def test_keywords_extracted(self):
        chars = self.tool._analyze_characteristics(
            "minimizar el costo sujeto a restricciones de capacidad y presupuesto"
        )
        keywords = chars["detected_keywords"]
        assert "minimización" in keywords
        assert "costos" in keywords
        assert "capacidad" in keywords or "presupuesto" in keywords


class TestFormatClassification:
    def test_format_with_characteristics(self):
        classification = {
            "type": "LP",
            "full_name": "Programación Lineal (Linear Programming)",
            "agent": "Agente de Programación Lineal",
            "agent_type": "linear_programming",
            "reason": "Linear relationships",
        }
        characteristics = {
            "has_integer_vars": False,
            "has_binary_vars": False,
            "has_nonlinear": False,
            "has_continuous_vars": True,
            "has_network_structure": False,
            "has_uncertainty": False,
            "detected_keywords": ["minimización", "costos"],
        }
        result = ProblemClassifierTool._format_classification(
            classification, characteristics
        )
        assert "LP" in result
        assert "Variables continuas" in result
        assert "minimización" in result

    def test_format_no_characteristics(self):
        classification = {
            "type": "LP",
            "full_name": "Programación Lineal",
            "agent": "Agente LP",
            "agent_type": "linear_programming",
            "reason": "Default",
        }
        characteristics = {
            "has_integer_vars": False,
            "has_binary_vars": False,
            "has_nonlinear": False,
            "has_continuous_vars": False,
            "has_network_structure": False,
            "has_uncertainty": False,
            "detected_keywords": [],
        }
        result = ProblemClassifierTool._format_classification(
            classification, characteristics
        )
        assert "Ninguna característica especial" in result


class TestCheckMethods:
    def test_check_integer_spanish(self):
        assert ProblemClassifierTool._check_integer_vars("necesito 5 camiones") is True

    def test_check_integer_english(self):
        assert (
            ProblemClassifierTool._check_integer_vars("integer variables needed")
            is True
        )

    def test_check_binary_spanish(self):
        assert (
            ProblemClassifierTool._check_binary_vars(
                "decisión binaria de abrir o cerrar"
            )
            is True
        )

    def test_check_nonlinear(self):
        assert (
            ProblemClassifierTool._check_nonlinearity("minimizar el costo cuadrático")
            is True
        )

    def test_check_continuous(self):
        assert (
            ProblemClassifierTool._check_continuous_vars("medir en kilogramos") is True
        )

    def test_check_network(self):
        assert ProblemClassifierTool._check_network("flujo en la red de nodos") is True

    def test_check_uncertainty(self):
        assert (
            ProblemClassifierTool._check_uncertainty("demanda con incertidumbre")
            is True
        )

    def test_no_match(self):
        assert ProblemClassifierTool._check_integer_vars("hello world") is False
