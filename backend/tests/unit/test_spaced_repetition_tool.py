"""
Unit tests for SpacedRepetitionReviewTool — start_review and complete_review actions.
"""

import json
from unittest.mock import MagicMock, patch

from app.tools.spaced_repetition_tool import SpacedRepetitionReviewTool


def make_tool(student_id=1):
    """Create a SpacedRepetitionReviewTool with mocked DB session."""
    db = MagicMock()
    return SpacedRepetitionReviewTool(db=db, student_id=student_id)


class TestInputParsing:
    def test_invalid_json(self):
        tool = make_tool()
        result = tool._run("not json")
        data = json.loads(result)
        assert data["status"] == "error"

    def test_non_dict(self):
        tool = make_tool()
        result = tool._run(json.dumps([1, 2]))
        data = json.loads(result)
        assert data["status"] == "error"

    def test_unknown_action(self):
        tool = make_tool()
        result = tool._run(json.dumps({"action": "destroy"}))
        data = json.loads(result)
        assert data["status"] == "error"
        assert "no reconocida" in data["message"]


class TestStartReview:
    def test_missing_concept_id(self):
        tool = make_tool()
        result = tool._run(json.dumps({"action": "start_review"}))
        data = json.loads(result)
        assert data["status"] == "error"
        assert "concept_id" in data["message"]

    @patch(
        "app.tools.spaced_repetition_tool.SpacedRepetitionReviewTool._action_start_review"
    )
    def test_start_review_not_found(self, mock_start):
        mock_start.return_value = json.dumps(
            {"status": "error", "message": "Not found"}
        )
        tool = make_tool()
        result = tool._run(
            json.dumps({"action": "start_review", "concept_id": "lp.simplex"})
        )
        data = json.loads(result)
        assert data["status"] == "error"

    def test_no_competency_found(self):
        tool = make_tool()
        tool.db.query.return_value.filter.return_value.first.return_value = None
        result = tool._run(
            json.dumps({"action": "start_review", "concept_id": "lp.simplex"})
        )
        data = json.loads(result)
        assert data["status"] == "error"
        assert "competencia" in data["message"]


class TestCompleteReview:
    def test_missing_concept_id(self):
        tool = make_tool()
        result = tool._run(json.dumps({"action": "complete_review"}))
        data = json.loads(result)
        assert data["status"] == "error"
        assert "concept_id" in data["message"]

    def test_missing_performance(self):
        tool = make_tool()
        result = tool._run(
            json.dumps({"action": "complete_review", "concept_id": "lp.simplex"})
        )
        data = json.loads(result)
        assert data["status"] == "error"
        assert "performance_quality" in data["message"]

    def test_invalid_performance_type(self):
        tool = make_tool()
        result = tool._run(
            json.dumps(
                {
                    "action": "complete_review",
                    "concept_id": "lp.simplex",
                    "performance_quality": "abc",
                }
            )
        )
        data = json.loads(result)
        assert data["status"] == "error"
        assert "entero" in data["message"]

    def test_performance_out_of_range(self):
        tool = make_tool()
        result = tool._run(
            json.dumps(
                {
                    "action": "complete_review",
                    "concept_id": "lp.simplex",
                    "performance_quality": 6,
                }
            )
        )
        data = json.loads(result)
        assert data["status"] == "error"
        assert "entre 0 y 5" in data["message"]

    def test_performance_negative(self):
        tool = make_tool()
        result = tool._run(
            json.dumps(
                {
                    "action": "complete_review",
                    "concept_id": "lp.simplex",
                    "performance_quality": -1,
                }
            )
        )
        data = json.loads(result)
        assert data["status"] == "error"
