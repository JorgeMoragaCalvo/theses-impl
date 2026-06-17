"""
Unit tests for LinearProgrammingAgent._select_tool_choice routing.

These guard the fix where a plain "resuélveme este problema" used to produce
narrated raw JSON instead of an actual solver call. The agent must now force a
concrete tool per the documented precedence: simplex_solver (símplex / tableaus
/ "paso a paso") -> region_visualizer (explicit graphical request) ->
problem_solver (plain solve).
"""

from unittest.mock import patch


def _make_agent():
    with patch("app.agents.base_agent.get_llm_service"):
        from app.agents.linear_programming_agent import LinearProgrammingAgent

        return LinearProgrammingAgent()


def _choice(agent, text: str) -> str | None:
    return agent._select_tool_choice([{"role": "user", "content": text}], {})


class TestLPToolChoice:
    def setup_method(self):
        self.agent = _make_agent()

    def test_plain_solve_forces_problem_solver(self):
        assert _choice(self.agent, "Resuélveme este problema") == "problem_solver"

    def test_solucion_optima_forces_problem_solver(self):
        assert _choice(self.agent, "¿Cuál es la solución óptima?") == "problem_solver"

    def test_simplex_forces_simplex_solver(self):
        assert (
            _choice(self.agent, "Resuélvelo con el método símplex")
            == "simplex_solver"
        )

    def test_step_by_step_forces_simplex_solver(self):
        assert _choice(self.agent, "Resuélvelo paso a paso") == "simplex_solver"

    def test_explicit_graphical_forces_region_visualizer(self):
        assert (
            _choice(self.agent, "Grafica la región factible")
            == "region_visualizer"
        )

    def test_graphical_step_by_step_prefers_region_visualizer(self):
        # "método gráfico" must win over the bare "paso a paso" simplex fallback.
        assert (
            _choice(self.agent, "Explícame el método gráfico paso a paso")
            == "region_visualizer"
        )

    def test_conceptual_question_forces_nothing(self):
        assert _choice(self.agent, "¿Por qué funciona la dualidad?") is None

    def test_conceptual_optimo_does_not_force(self):
        # Bare "óptimo" is conceptual-leaky; must NOT force a solver.
        assert _choice(self.agent, "¿Por qué este vértice es óptimo?") is None

    def test_cual_es_el_optimo_forces_problem_solver(self):
        assert _choice(self.agent, "¿Cuál es el óptimo?") == "problem_solver"
