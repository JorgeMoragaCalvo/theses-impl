"""
Unit tests for agent topic detection and off-topic responses.
"""

from unittest.mock import patch


class TestLinearProgrammingTopicCheck:
    def setup_method(self):
        with patch("app.agents.base_agent.get_llm_service"):
            from app.agents.linear_programming_agent import LinearProgrammingAgent

            self.agent = LinearProgrammingAgent()

    def test_lp_keyword_detected(self):
        assert self.agent.is_topic_related("Explica el método simplex") is True

    def test_english_keyword(self):
        assert self.agent.is_topic_related("What is linear programming?") is True

    def test_off_topic(self):
        assert self.agent.is_topic_related("How's the weather?") is False

    def test_off_topic_response(self):
        response = self.agent._get_off_topic_response()
        assert "Programación Lineal" in response

    def test_strategies(self):
        strategies = self.agent.get_available_strategies()
        assert len(strategies) >= 4


class TestIntegerProgrammingTopicCheck:
    def setup_method(self):
        with patch("app.agents.base_agent.get_llm_service"):
            from app.agents.integer_programming_agent import IntegerProgrammingAgent

            self.agent = IntegerProgrammingAgent()

    def test_ip_keyword(self):
        assert self.agent.is_topic_related("branch and bound algorithm") is True

    def test_off_topic(self):
        assert self.agent.is_topic_related("Tell me a joke") is False

    def test_off_topic_response(self):
        response = self.agent._get_off_topic_response()
        assert "Programación Entera" in response


class TestNlpAgentTopicCheck:
    def setup_method(self):
        with patch("app.agents.base_agent.get_llm_service"):
            from app.agents.nlp_agent import NonLinearProgrammingAgent

            self.agent = NonLinearProgrammingAgent()

    def test_nlp_keyword(self):
        assert self.agent.is_topic_related("condiciones KKT") is True

    def test_off_topic(self):
        assert self.agent.is_topic_related("Make me a sandwich") is False


class TestMathModelingTopicCheck:
    def setup_method(self):
        with patch("app.agents.base_agent.get_llm_service"):
            from app.agents.mathematical_modeling_agent import MathematicalModelingAgent

            self.agent = MathematicalModelingAgent()

    def test_modeling_keyword(self):
        assert self.agent.is_topic_related("formulación del modelo matemático") is True

    def test_off_topic(self):
        assert self.agent.is_topic_related("Who won the World Cup?") is False


class TestORAgentTopicCheck:
    def setup_method(self):
        with patch("app.agents.base_agent.get_llm_service"):
            from app.agents.operations_research_agent import OperationsResearchAgent

            self.agent = OperationsResearchAgent()

    def test_or_keyword(self):
        assert self.agent.is_topic_related("investigación de operaciones") is True

    def test_off_topic(self):
        assert self.agent.is_topic_related("Python decorators") is False
