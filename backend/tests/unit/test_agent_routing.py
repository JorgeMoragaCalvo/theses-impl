"""
Unit tests for agent registry and routing (app.main).
"""

from app.main import AGENT_REGISTRY, get_agent_for_topic


class TestAgentRegistry:

    def test_registry_has_all_topics(self):
        expected = {
            "operations_research",
            "linear_programming",
            "mathematical_modeling",
            "nonlinear_programming",
            "integer_programming",
        }
        assert set(AGENT_REGISTRY.keys()) == expected

    def test_get_agent_valid_topic(self):
        """Each registered topic returns a non-None agent."""
        for topic in AGENT_REGISTRY:
            agent = get_agent_for_topic(topic)
            assert agent is not None

    def test_get_agent_unknown_fallback(self):
        """The unknown topic falls back to the linear programming agent."""
        agent = get_agent_for_topic("quantum_computing")
        # Should be a LinearProgrammingAgent instance
        from app.agents.linear_programming_agent import LinearProgrammingAgent
        assert isinstance(agent, LinearProgrammingAgent)
