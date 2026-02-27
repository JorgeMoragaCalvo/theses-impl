"""
Integration tests for /auth/* endpoints.
"""


class TestRegister:

    def test_register_usach_domain(self, client):
        """POST /auth/register with @usach.cl → 201 + access_token."""
        resp = client.post("/auth/register", json={
            "name": "New USACH Student",
            "email": "newstudent@usach.cl",
            "password": "securepass123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["is_active"] is True

    def test_register_other_domain_pending(self, client):
        """@gmail.com → 201 + pending_approval status."""
        resp = client.post("/auth/register", json={
            "name": "External Student",
            "email": "external@gmail.com",
            "password": "securepass123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending_approval"

    def test_register_duplicate_email(self, client, test_user):
        """Duplicate email → 400."""
        resp = client.post("/auth/register", json={
            "name": "Duplicate",
            "email": "student@usach.cl",
            "password": "securepass123",
        })
        assert resp.status_code == 400


class TestLogin:

    def test_login_success(self, client, test_user):
        """Correct credentials → 200 + token."""
        resp = client.post("/auth/login", json={
            "email": "student@usach.cl",
            "password": "testpassword123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    def test_login_wrong_password(self, client, test_user):
        """Wrong password → 401."""
        resp = client.post("/auth/login", json={
            "email": "student@usach.cl",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401


class TestGetMe:

    def test_authenticated(self, client, auth_headers):
        """GET /auth/me with valid token → 200 + user data."""
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "student@usach.cl"

    def test_no_token(self, client):
        """GET /auth/me without a token → 401/403."""
        resp = client.get("/auth/me")
        assert resp.status_code in (401, 403)
