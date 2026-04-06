"""
Extended integration tests for assessment endpoints — covers list/get/not-found paths.
"""

from datetime import datetime, timezone

from app.database import Assessment
from app.enums import Topic


def _create_assessment(test_db, student_id, submitted=False):
    a = Assessment(
        student_id=student_id,
        topic=Topic.LINEAR_PROGRAMMING,
        question="What is LP?",
        correct_answer="Linear Programming is...",
        rubric="Grade fairly",
        max_score=7.0,
    )
    if submitted:
        a.student_answer = "My answer"
        a.submitted_at = datetime.now(timezone.utc)
    test_db.add(a)
    test_db.commit()
    test_db.refresh(a)
    return a


class TestListAssessments:
    def test_list_own_assessments(self, client, auth_headers, test_db, test_user):
        _create_assessment(test_db, test_user.id)
        resp = client.get(
            f"/students/{test_user.id}/assessments",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_list_with_topic_filter(self, client, auth_headers, test_db, test_user):
        _create_assessment(test_db, test_user.id)
        resp = client.get(
            f"/students/{test_user.id}/assessments?topic=linear_programming",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_other_student_forbidden(self, client, auth_headers, test_admin):
        resp = client.get(
            f"/students/{test_admin.id}/assessments",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_nonexistent_student(self, client, admin_auth_headers):
        resp = client.get(
            "/students/99999/assessments",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 404


class TestGetAssessment:
    def test_get_own(self, client, auth_headers, test_db, test_user):
        a = _create_assessment(test_db, test_user.id)
        resp = client.get(f"/assessments/{a.id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == a.id

    def test_not_found(self, client, auth_headers):
        resp = client.get("/assessments/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_other_student_forbidden(self, client, auth_headers, test_db, test_admin):
        a = _create_assessment(test_db, test_admin.id)
        resp = client.get(f"/assessments/{a.id}", headers=auth_headers)
        assert resp.status_code == 403


class TestSubmitNotFound:
    def test_submit_not_found(self, client, auth_headers):
        resp = client.post(
            "/assessments/99999/submit",
            json={"student_answer": "answer"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestGradeEdgeCases:
    def test_grade_not_found(self, client, admin_auth_headers):
        resp = client.post(
            "/assessments/99999/grade",
            json={"score": 5.0, "feedback": "OK"},
            headers=admin_auth_headers,
        )
        assert resp.status_code == 404

    def test_grade_not_submitted(self, client, admin_auth_headers, test_db, test_user):
        a = _create_assessment(test_db, test_user.id, submitted=False)
        resp = client.post(
            f"/assessments/{a.id}/grade",
            json={"score": 5.0, "feedback": "OK"},
            headers=admin_auth_headers,
        )
        assert resp.status_code == 400
