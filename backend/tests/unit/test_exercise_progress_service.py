"""
Unit tests for app.services.exercise_progress_service — pure functions.
"""

from app.services.exercise_progress_service import compute_max_unlocked_rank


class TestComputeMaxUnlockedRank:
    def test_no_ranked_exercises(self):
        """All rank-0 exercises → returns 0."""
        exercises = [
            {"id": "ex1", "rank": 0},
            {"id": "ex2", "rank": 0},
        ]
        assert compute_max_unlocked_rank(set(), exercises) == 0

    def test_base_no_completions(self):
        """Ranked exercises but nothing completed → rank 1 always unlocked."""
        exercises = [
            {"id": "ex1", "rank": 1},
            {"id": "ex2", "rank": 2},
        ]
        assert compute_max_unlocked_rank(set(), exercises) == 1

    def test_progression(self):
        """Rank 1 completed → unlocks rank 2."""
        exercises = [
            {"id": "ex1", "rank": 1},
            {"id": "ex2", "rank": 2},
            {"id": "ex3", "rank": 3},
        ]
        completed = {"ex1"}
        assert compute_max_unlocked_rank(completed, exercises) == 2

    def test_gap_stops_progression(self):
        """Rank 1 done, rank 2 not done → stops at rank 2 (doesn't skip to 3)."""
        exercises = [
            {"id": "ex1", "rank": 1},
            {"id": "ex2", "rank": 2},
            {"id": "ex3", "rank": 3},
        ]
        completed = {"ex1"}  # rank 2 isn't completed
        result = compute_max_unlocked_rank(completed, exercises)
        assert result == 2  # rank 2 is unlocked but rank 3 is not

    def test_full_progression(self):
        """All ranks completed → unlocks beyond max rank."""
        exercises = [
            {"id": "ex1", "rank": 1},
            {"id": "ex2", "rank": 2},
        ]
        completed = {"ex1", "ex2"}
        assert compute_max_unlocked_rank(completed, exercises) == 3

    def test_empty_exercises(self):
        """No exercises at all → returns 0."""
        assert compute_max_unlocked_rank(set(), []) == 0
