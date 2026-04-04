"""
Integration tests for /students/* endpoints.
"""


class TestGetStudent:

    def test_get_own_profile(self, client, auth_headers, test_user):
        resp = client.get(f"/students/{test_user.id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "student@usach.cl"

    def test_get_other_profile_forbidden(self, client, auth_headers, test_admin):
        resp = client.get(f"/students/{test_admin.id}", headers=auth_headers)
        assert resp.status_code == 403

    def test_get_nonexistent(self, client, admin_auth_headers):
        resp = client.get("/students/99999", headers=admin_auth_headers)
        assert resp.status_code == 404


class TestUpdateStudent:

    def test_update_own_name(self, client, auth_headers, test_user):
        resp = client.put(
            f"/students/{test_user.id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_update_other_forbidden(self, client, auth_headers, test_admin):
        resp = client.put(
            f"/students/{test_admin.id}",
            json={"name": "Hacked"},
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_update_knowledge_levels(self, client, auth_headers, test_user):
        new_levels = {
            "operations_research": "intermediate",
            "mathematical_modeling": "beginner",
            "linear_programming": "advanced",
            "integer_programming": "beginner",
            "nonlinear_programming": "beginner",
        }
        resp = client.put(
            f"/students/{test_user.id}",
            json={"knowledge_levels": new_levels},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["knowledge_levels"]["linear_programming"] == "advanced"


class TestListStudents:

    def test_admin_can_list(self, client, admin_auth_headers, test_admin):
        resp = client.get("/students", headers=admin_auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_non_admin_forbidden(self, client, auth_headers):
        resp = client.get("/students", headers=auth_headers)
        assert resp.status_code == 403


class TestCreateStudent:

    def test_non_admin_forbidden(self, client, auth_headers):
        resp = client.post(
            "/students",
            json={"name": "No", "email": "no@usach.cl"},
            headers=auth_headers,
        )
        assert resp.status_code == 403


class TestGetStudentProgress:

    def test_get_own_progress(self, client, auth_headers, test_user):
        resp = client.get(f"/students/{test_user.id}/progress", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_conversations" in data

    def test_other_progress_forbidden(self, client, auth_headers, test_admin):
        resp = client.get(f"/students/{test_admin.id}/progress", headers=auth_headers)
        assert resp.status_code == 403
