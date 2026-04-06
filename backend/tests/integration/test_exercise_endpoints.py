"""
Integration tests for /exercises/* endpoints.
"""


class TestListExercises:
    def test_list_all(self, client):
        resp = client.get("/exercises")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_by_topic(self, client):
        resp = client.get("/exercises?topic=linear_programming")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestGetExercisePreview:
    def test_nonexistent_exercise(self, client):
        resp = client.get("/exercises/nonexistent_99")
        assert resp.status_code == 404
