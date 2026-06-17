"""
Unit tests for IntegerProgrammingAgent._select_tool_choice routing.

These guard the fix where a plain "resuélveme este problema" used to produce
narrated raw JSON instead of an actual solver call. The agent must now force a
concrete tool per the documented precedence: branch_and_bound (integer tree) ->
simplex_solver (LP-relaxation steps) -> problem_solver (plain solve) ->
region_visualizer (explicit graphical request only).
"""

from unittest.mock import patch


def _make_agent():
    with patch("app.agents.base_agent.get_llm_service"):
        from app.agents.integer_programming_agent import IntegerProgrammingAgent

        return IntegerProgrammingAgent()


def _choice(agent, text: str) -> str | None:
    return agent._select_tool_choice([{"role": "user", "content": text}], {})


class TestIPToolChoice:
    def setup_method(self):
        self.agent = _make_agent()

    def test_plain_solve_forces_problem_solver(self):
        assert _choice(self.agent, "Resuélveme este problema") == "problem_solver"

    def test_solucion_optima_forces_problem_solver(self):
        assert _choice(self.agent, "¿Cuál es la solución óptima?") == "problem_solver"

    def test_explicit_branch_and_bound(self):
        assert (
            _choice(self.agent, "Muéstrame el árbol de branch and bound")
            == "branch_and_bound"
        )

    def test_step_by_step_integer_forces_branch_and_bound(self):
        assert (
            _choice(self.agent, "Resuélvelo paso a paso, es un problema entero")
            == "branch_and_bound"
        )

    def test_lp_relaxation_simplex_forces_simplex_solver(self):
        assert (
            _choice(self.agent, "Muéstrame la relajación LP paso a paso con símplex")
            == "simplex_solver"
        )

    def test_explicit_graphical_forces_region_visualizer(self):
        assert (
            _choice(self.agent, "Grafica la región factible")
            == "region_visualizer"
        )

    def test_conceptual_question_forces_nothing(self):
        assert _choice(self.agent, "¿Por qué la relajación LP da una cota?") is None

    def test_conceptual_optimo_does_not_force(self):
        # Bare "óptimo" is conceptual-leaky; must NOT force a solver.
        assert _choice(self.agent, "¿Por qué este vértice es óptimo?") is None

    def test_cual_es_el_optimo_forces_problem_solver(self):
        assert _choice(self.agent, "¿Cuál es el óptimo?") == "problem_solver"