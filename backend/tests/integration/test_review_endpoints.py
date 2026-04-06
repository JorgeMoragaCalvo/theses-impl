"""
Integration tests for /reviews/* and /students/{id}/reviews/* endpoints.
"""


class TestGetDueReviews:
    def test_get_own_due_reviews(self, client, auth_headers, test_user):
        resp = client.get(
            f"/students/{test_user.id}/reviews/due",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["student_id"] == test_user.id
        assert isinstance(data["due_reviews"], list)

    def test_other_student_forbidden(self, client, auth_headers, test_admin):
        resp = client.get(
            f"/students/{test_admin.id}/reviews/due",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_nonexistent_student(self, client, admin_auth_headers):
        resp = client.get(
            "/students/99999/reviews/due",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 404

    def test_with_topic_filter(self, client, auth_headers, test_user):
        resp = client.get(
            f"/students/{test_user.id}/reviews/due?topic=linear_programming",
            headers=auth_headers,
        )
        assert resp.status_code == 200


class TestStartReview:
    def test_other_student_forbidden(self, client, admin_auth_headers, test_user):
        resp = client.post(
            f"/students/{test_user.id}/reviews/start",
            json={"concept_id": "lp.simplex"},
            headers=admin_auth_headers,
        )
        assert resp.status_code == 403

    def test_no_competency_record(self, client, auth_headers, test_user):
        resp = client.post(
            f"/students/{test_user.id}/reviews/start",
            json={"concept_id": "nonexistent.concept"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestCompleteReview:
    def test_review_not_found(self, client, auth_headers):
        resp = client.post(
            "/reviews/99999/complete",
            json={"performance_quality": 4},
            headers=auth_headers,
        )
        assert resp.status_code == 404
