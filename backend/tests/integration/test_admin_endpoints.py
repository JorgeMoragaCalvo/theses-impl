"""
Integration tests for /admin/* endpoints.
"""


class TestListUsers:
    def test_list_users_admin(self, client, admin_auth_headers, test_admin):
        """Admin can list users → 200."""
        resp = client.get("/admin/users", headers=admin_auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the admin user

    def test_list_users_non_admin(self, client, auth_headers):
        """Non-admin → 403."""
        resp = client.get("/admin/users", headers=auth_headers)
        assert resp.status_code == 403


class TestUpdateUserStatus:
    def test_activate_deactivate(self, client, admin_auth_headers, test_db, test_user):
        """Admin can deactivate and activate a user."""
        # Deactivate
        resp = client.put(
            f"/admin/users/{test_user.id}/status?is_active=false",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

        # Re-activate
        resp = client.put(
            f"/admin/users/{test_user.id}/status?is_active=true",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True


class TestSystemStats:
    def test_system_stats(self, client, admin_auth_headers, test_admin):
        """GET /admin/stats → 200 with expected keys."""
        resp = client.get("/admin/stats", headers=admin_auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "total_conversations" in data
        assert "total_assessments" in data
