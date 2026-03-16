"""
Integration tests for assessment endpoints.
"""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.database import Assessment
from app.enums import Topic


class TestGenerateAssessment:

    def test_generate_assessment(self, client, auth_headers, test_db, test_user):
        """POST /assessments/generate → 201."""
        with patch("app.routers.assessments.get_assessment_service") as mock_svc:
            mock_instance = MagicMock()
            mock_instance.generate_personalized_assessment.return_value = {
                "question": "What is LP?",
                "correct_answer": "Linear programming is...",
                "rubric": "Accuracy 4pts",
                "metadata": {},
            }
            mock_svc.return_value = mock_instance

            resp = client.post("/assessments/generate", headers=auth_headers, json={
                "topic": "linear_programming",
                "difficulty": "intermediate",
            })
            assert resp.status_code == 201
            data = resp.json()
            assert data["question"] == "What is LP?"


class TestSubmitAssessment:

    @staticmethod
    def _create_assessment(test_db, student_id):
        """Helper to create an unsubmitted assessment."""
        a = Assessment(
            student_id=student_id,
            topic=Topic.LINEAR_PROGRAMMING,
            question="Test question",
            correct_answer="Correct answer",
            rubric="Grade fairly",
            max_score=7.0,
        )
        test_db.add(a)
        test_db.commit()
        test_db.refresh(a)
        return a

    def test_submit_assessment(self, client, auth_headers, test_db, test_user):
        """POST /assessments/{id}/submit → graded response."""
        assessment = self._create_assessment(test_db, test_user.id)

        with patch("app.routers.assessments.get_grading_service") as mock_gs:
            mock_grading = MagicMock()
            mock_grading.grade_assessment.return_value = (5.0, "Good work")
            mock_gs.return_value = mock_grading

            resp = client.post(
                f"/assessments/{assessment.id}/submit",
                headers=auth_headers,
                json={"student_answer": "My answer"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["student_answer"] == "My answer"

    def test_submit_already_submitted(self, client, auth_headers, test_db, test_user):
        """Re-submitting → 400."""
        assessment = self._create_assessment(test_db, test_user.id)
        assessment.submitted_at = datetime.now(timezone.utc)
        test_db.commit()

        resp = client.post(
            f"/assessments/{assessment.id}/submit",
            headers=auth_headers,
            json={"student_answer": "My answer"},
        )
        assert resp.status_code == 400


class TestGradeAssessment:

    def test_grade_admin_only(self, client, auth_headers, admin_auth_headers, test_db, test_user):
        """Non-admin → 403, admin → 200."""
        # Create a submitted assessment
        a = Assessment(
            student_id=test_user.id,
            topic=Topic.LINEAR_PROGRAMMING,
            question="Test",
            student_answer="Answer",
            correct_answer="Correct",
            rubric="Rubric",
            max_score=7.0,
            submitted_at=datetime.now(timezone.utc),
        )
        test_db.add(a)
        test_db.commit()
        test_db.refresh(a)

        grade_payload = {"score": 6.0, "feedback": "Well done"}

        # Non-admin should be forbidden
        resp = client.post(
            f"/assessments/{a.id}/grade",
            headers=auth_headers,
            json=grade_payload,
        )
        assert resp.status_code == 403

        # Admin should succeed
        resp = client.post(
            f"/assessments/{a.id}/grade",
            headers=admin_auth_headers,
            json=grade_payload,
        )
        assert resp.status_code == 200
        assert resp.json()["score"] == 6.0
