"""
Integration tests for /analytics/events endpoint.
"""


class TestRecordEvents:
    def test_record_events(self, client, auth_headers):
        resp = client.post(
            "/analytics/events",
            json={
                "events": [
                    {
                        "session_id": "sess-123",
                        "event_category": "page_visit",
                        "event_action": "page_view",
                        "page_name": "chat",
                    },
                ]
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["recorded"] >= 1

    def test_requires_auth(self, client):
        resp = client.post(
            "/analytics/events",
            json={
                "events": [
                    {
                        "session_id": "sess-123",
                        "event_category": "page_visit",
                        "event_action": "page_view",
                    },
                ]
            },
        )
        assert resp.status_code in (401, 403)
