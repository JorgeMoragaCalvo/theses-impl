"""
Unit tests for GradingService — parse logic and prompt building.
"""

from unittest.mock import MagicMock, patch

from app.services.grading_service import GradingService


class TestParseGradingResponse:
    @staticmethod
    def _make_service():
        db = MagicMock()
        with patch("app.services.grading_service.get_llm_service") as mock_llm:
            mock_llm.return_value = MagicMock()
            return GradingService(db)

    def test_parse_valid_json_response(self):
        svc = self._make_service()
        response = '{"score": 5.5, "feedback": "Bien hecho", "concepts_tested": ["lp.simplex"]}'
        score, feedback, concepts = svc.parse_grading_response(response, max_score=7.0)
        assert score == 5.5
        assert feedback == "Bien hecho"
        assert "lp.simplex" in concepts

    def test_parse_score_clamped(self):
        """Score exceeding max_score gets clamped."""
        svc = self._make_service()
        response = '{"score": 10.0, "feedback": "Perfect"}'
        score, feedback, _ = svc.parse_grading_response(response, max_score=7.0)
        assert score == 7.0

    def test_parse_score_below_minimum(self):
        """Score below 1.0 gets clamped to 1.0."""
        svc = self._make_service()
        response = '{"score": 0.0, "feedback": "Needs work"}'
        score, _, _ = svc.parse_grading_response(response, max_score=7.0)
        assert score == 1.0

    def test_parse_fallback_regex(self):
        """Non-JSON with a 'score: 5.0' pattern falls back to regex."""
        svc = self._make_service()
        response = "The student scored score: 5.0 points. feedback: Good effort."
        score, feedback, concepts = svc.parse_grading_response(response, max_score=7.0)
        assert score == 5.0
        assert len(concepts) == 0  # Fallback doesn't extract concepts


class TestBuildGradingPrompt:
    def test_includes_rubric(self):
        prompt = GradingService.build_grading_prompt(
            question="What is LP?",
            student_answer="Linear programming is...",
            correct_answer="LP is a method...",
            rubric="Accuracy 4pts, Completeness 3pts",
            max_score=7.0,
            topic="linear_programming",
        )
        assert "What is LP?" in prompt
        assert "Linear programming is..." in prompt
        assert "LP is a method..." in prompt
        assert "Accuracy 4pts, Completeness 3pts" in prompt
        assert "7.0" in prompt

    def test_includes_concepts_section(self):
        prompt = GradingService.build_grading_prompt(
            question="Q",
            student_answer="A",
            correct_answer="C",
            rubric="R",
            max_score=7.0,
            topic="linear_programming",
            available_concepts=["lp.simplex", "lp.dual"],
        )
        assert "lp.simplex" in prompt
        assert "lp.dual" in prompt
        assert "concepts_tested" in prompt
