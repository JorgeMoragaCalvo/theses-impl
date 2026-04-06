"""
Integration tests for /feedback endpoint.
"""

from app.database import Conversation, Message
from app.enums import MessageRole, Topic


class TestCreateFeedback:
    def _create_conversation_and_message(self, test_db, user_id):
        """Helper: create a conversation with one assistant message."""
        conv = Conversation(
            student_id=user_id,
            topic=Topic.LINEAR_PROGRAMMING,
        )
        test_db.add(conv)
        test_db.flush()

        msg = Message(
            conversation_id=conv.id,
            role=MessageRole.ASSISTANT,
            content="Here is the simplex explanation.",
        )
        test_db.add(msg)
        test_db.commit()
        test_db.refresh(msg)
        return conv, msg

    def test_create_feedback(self, client, auth_headers, test_db, test_user):
        _, msg = self._create_conversation_and_message(test_db, test_user.id)
        resp = client.post(
            "/feedback",
            json={
                "message_id": msg.id,
                "rating": 5,
                "is_helpful": True,
                "comment": "Great!",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["rating"] == 5
        assert data["is_helpful"] is True

    def test_message_not_found(self, client, auth_headers):
        resp = client.post(
            "/feedback",
            json={"message_id": 99999, "rating": 3},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_other_users_message_forbidden(
        self, client, admin_auth_headers, test_db, test_user
    ):
        """Admin tries to leave feedback on a student's conversation → 403."""
        _, msg = self._create_conversation_and_message(test_db, test_user.id)
        resp = client.post(
            "/feedback",
            json={"message_id": msg.id, "rating": 4},
            headers=admin_auth_headers,
        )
        assert resp.status_code == 403
