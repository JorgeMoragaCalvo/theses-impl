"""
Integration tests for /students/{id}/competencies, /mastery, /recommended-concepts.
"""


class TestGetCompetencies:
    def test_requires_topic_param(self, client, auth_headers, test_user):
        resp = client.get(
            f"/students/{test_user.id}/competencies",
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "topic" in resp.json()["detail"].lower()

    def test_with_topic(self, client, auth_headers, test_user):
        resp = client.get(
            f"/students/{test_user.id}/competencies?topic=linear_programming",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["student_id"] == test_user.id

    def test_other_student_forbidden(self, client, auth_headers, test_admin):
        resp = client.get(
            f"/students/{test_admin.id}/competencies?topic=linear_programming",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_nonexistent_student(self, client, admin_auth_headers):
        resp = client.get(
            "/students/99999/competencies?topic=linear_programming",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 404


class TestGetMastery:
    def test_own_mastery(self, client, auth_headers, test_user):
        resp = client.get(
            f"/students/{test_user.id}/mastery/linear_programming",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_other_student_forbidden(self, client, auth_headers, test_admin):
        resp = client.get(
            f"/students/{test_admin.id}/mastery/linear_programming",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_nonexistent_student(self, client, admin_auth_headers):
        resp = client.get(
            "/students/99999/mastery/linear_programming",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 404


class TestGetRecommendedConcepts:
    def test_own_recommendations(self, client, auth_headers, test_user):
        resp = client.get(
            f"/students/{test_user.id}/recommended-concepts/linear_programming",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_other_student_forbidden(self, client, auth_headers, test_admin):
        resp = client.get(
            f"/students/{test_admin.id}/recommended-concepts/linear_programming",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_nonexistent_student(self, client, admin_auth_headers):
        resp = client.get(
            "/students/99999/recommended-concepts/linear_programming",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 404
