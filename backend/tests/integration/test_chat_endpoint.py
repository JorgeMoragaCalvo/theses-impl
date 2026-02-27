"""
Integration tests for POST /chat endpoint.
"""
from unittest.mock import MagicMock, patch


class TestChatEndpoint:

    def test_chat_creates_conversation(self, client, auth_headers):
        """POST /chat → creates a new conversation and returns conversation_id."""
        with patch("app.main.get_agent_for_topic") as mock_get_agent:
            mock_agent = MagicMock()
            mock_agent.generate_response.return_value = "Hello student!"
            mock_agent.agent_type = "linear_programming"
            mock_get_agent.return_value = mock_agent

            resp = client.post("/chat", headers=auth_headers, json={
                "message": "Explain simplex",
                "topic": "linear_programming",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert "conversation_id" in data
            assert data["conversation_id"] > 0

    def test_chat_returns_response(self, client, auth_headers):
        """Response includes message content."""
        with patch("app.main.get_agent_for_topic") as mock_get_agent:
            mock_agent = MagicMock()
            mock_agent.generate_response.return_value = "The simplex method is..."
            mock_agent.agent_type = "linear_programming"
            mock_get_agent.return_value = mock_agent

            resp = client.post("/chat", headers=auth_headers, json={
                "message": "What is simplex?",
                "topic": "linear_programming",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["response"] == "The simplex method is..."

    def test_chat_unauthenticated(self, client):
        """POST /chat without a token → 401/403."""
        resp = client.post("/chat", json={
            "message": "Hello",
            "topic": "linear_programming",
        })
        assert resp.status_code in (401, 403)
