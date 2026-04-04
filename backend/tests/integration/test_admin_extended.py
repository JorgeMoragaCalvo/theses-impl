"""
Extended integration tests for /admin/* endpoints — covers analytics, settings, role updates.
"""


class TestGetUserDetails:

    def test_get_user(self, client, admin_auth_headers, test_user):
        resp = client.get(f"/admin/users/{test_user.id}", headers=admin_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == test_user.id

    def test_get_nonexistent_user(self, client, admin_auth_headers):
        resp = client.get("/admin/users/99999", headers=admin_auth_headers)
        assert resp.status_code == 404


class TestUpdateUserRole:

    def test_change_role_to_admin(self, client, admin_auth_headers, test_user):
        resp = client.put(
            f"/admin/users/{test_user.id}/role?role=admin",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    def test_invalid_role(self, client, admin_auth_headers, test_user):
        resp = client.put(
            f"/admin/users/{test_user.id}/role?role=superadmin",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 400

    def test_cannot_change_own_role(self, client, admin_auth_headers, test_admin):
        resp = client.put(
            f"/admin/users/{test_admin.id}/role?role=user",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 400

    def test_nonexistent_user(self, client, admin_auth_headers):
        resp = client.put(
            "/admin/users/99999/role?role=admin",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 404


class TestUpdateStatusExtended:

    def test_cannot_deactivate_self(self, client, admin_auth_headers, test_admin):
        resp = client.put(
            f"/admin/users/{test_admin.id}/status?is_active=false",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 400

    def test_nonexistent_user(self, client, admin_auth_headers):
        resp = client.put(
            "/admin/users/99999/status?is_active=false",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 404


class TestSystemSettings:

    def test_get_settings(self, client, admin_auth_headers):
        resp = client.get("/admin/settings", headers=admin_auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "llm_provider" in data
        assert "version" in data

    def test_non_admin_forbidden(self, client, auth_headers):
        resp = client.get("/admin/settings", headers=auth_headers)
        assert resp.status_code == 403


class TestAnalyticsEndpoints:

    def test_analytics_summary(self, client, admin_auth_headers):
        resp = client.get("/admin/analytics/summary", headers=admin_auth_headers)
        assert resp.status_code == 200

    def test_dau(self, client, admin_auth_headers):
        resp = client.get("/admin/analytics/dau", headers=admin_auth_headers)
        assert resp.status_code == 200

    def test_sessions(self, client, admin_auth_headers):
        resp = client.get("/admin/analytics/sessions", headers=admin_auth_headers)
        assert resp.status_code == 200

    def test_peak_hours(self, client, admin_auth_headers):
        resp = client.get("/admin/analytics/peak-hours", headers=admin_auth_headers)
        assert resp.status_code == 200

    def test_pages(self, client, admin_auth_headers):
        resp = client.get("/admin/analytics/pages", headers=admin_auth_headers)
        assert resp.status_code == 200

    def test_topics(self, client, admin_auth_headers):
        resp = client.get("/admin/analytics/topics", headers=admin_auth_headers)
        assert resp.status_code == 200

    def test_engagement(self, client, admin_auth_headers):
        resp = client.get("/admin/analytics/engagement", headers=admin_auth_headers)
        assert resp.status_code == 200

    def test_non_admin_forbidden(self, client, auth_headers):
        resp = client.get("/admin/analytics/summary", headers=auth_headers)
        assert resp.status_code == 403
