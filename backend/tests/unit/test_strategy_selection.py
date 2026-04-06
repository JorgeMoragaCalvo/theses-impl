"""
Unit tests for BaseAgent.select_explanation_strategy and build_adaptive_prompt_section.
"""

from app.agents.base_agent import BaseAgent

ALL_STRATEGIES = [
    "step-by-step",
    "example-based",
    "analogy-based",
    "conceptual",
    "formal-mathematical",
    "comparative",
]


class TestSelectExplanationStrategy:
    def test_high_confusion_selects_simple(self):
        strategy = BaseAgent.select_explanation_strategy(
            confusion_level="high",
            knowledge_level="advanced",
            previous_strategies=[],
            all_available_strategies=ALL_STRATEGIES,
        )
        assert strategy in ("step-by-step", "example-based", "analogy-based")

    def test_no_confusion_advanced_selects_formal(self):
        strategy = BaseAgent.select_explanation_strategy(
            confusion_level="none",
            knowledge_level="advanced",
            previous_strategies=[],
            all_available_strategies=ALL_STRATEGIES,
        )
        assert strategy in ("conceptual", "formal-mathematical", "comparative")

    def test_strategy_avoids_recent(self):
        """Should not repeat a recently used strategy if alternatives exist."""
        strategy = BaseAgent.select_explanation_strategy(
            confusion_level="high",
            knowledge_level="beginner",
            previous_strategies=["step-by-step"],
            all_available_strategies=ALL_STRATEGIES,
        )
        assert strategy != "step-by-step"

    def test_all_used_resets(self):
        """When all strategies were recently used, it resets and picks again."""
        strategy = BaseAgent.select_explanation_strategy(
            confusion_level="high",
            knowledge_level="beginner",
            previous_strategies=ALL_STRATEGIES,
            all_available_strategies=ALL_STRATEGIES,
        )
        assert strategy in ALL_STRATEGIES


class TestBuildAdaptivePromptSection:
    def test_high_confusion_contains_simplify(self):
        analysis = {"detected": True, "level": "high", "signals": ["high:no entiendo"]}
        result = BaseAgent.build_adaptive_prompt_section(analysis, "step-by-step")
        assert "SIMPLIFY" in result

    def test_no_confusion_empty(self):
        analysis = {"detected": False, "level": "none", "signals": []}
        result = BaseAgent.build_adaptive_prompt_section(analysis, "conceptual")
        # When there's no confusion, the adaptive section should be minimal
        assert "SIMPLIFY" not in result
