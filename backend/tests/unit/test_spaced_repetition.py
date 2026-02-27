"""
Unit tests for SpacedRepetitionService.calculate_next_review — SM-2 algorithm.
"""
from unittest.mock import MagicMock

import pytest
from app.services.spaced_repetition_service import (
    DEFAULT_EASE_FACTOR,
    MIN_EASE_FACTOR,
    SpacedRepetitionService,
)


def _make_competency(decay_factor=DEFAULT_EASE_FACTOR, correct_count=0,
                     next_review_at=None, last_correct_at=None):
    """Build a mock StudentCompetency with the fields SM-2 needs."""
    comp = MagicMock()
    comp.decay_factor = decay_factor
    comp.correct_count = correct_count
    comp.next_review_at = next_review_at
    comp.last_correct_at = last_correct_at
    return comp


class TestCalculateNextReview:

    def test_failed_recall_resets_interval(self):
        """Quality < 3 → an interval resets to 1 day."""
        comp = _make_competency()
        next_review, new_ease = SpacedRepetitionService.calculate_next_review(comp, 2)
        # Interval should be 1 day (INITIAL_INTERVALS[0])
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        delta = (next_review - now).total_seconds()
        assert 0 < delta <= 86400 + 5  # ~1 day, small tolerance

    def test_failed_recall_decreases_ease(self):
        """Quality < 3 → an ease factor decreases by 0.2."""
        comp = _make_competency(decay_factor=2.5)
        _, new_ease = SpacedRepetitionService.calculate_next_review(comp, 1)
        assert new_ease == pytest.approx(2.3, abs=0.01)

    def test_perfect_recall_increases_ease(self):
        """Quality 5 → an ease factor increases."""
        comp = _make_competency(decay_factor=2.5)
        _, new_ease = SpacedRepetitionService.calculate_next_review(comp, 5)
        assert new_ease > 2.5

    def test_ease_never_below_minimum(self):
        """Ease factor must never go below MIN_EASE_FACTOR (1.3)."""
        comp = _make_competency(decay_factor=MIN_EASE_FACTOR)
        _, new_ease = SpacedRepetitionService.calculate_next_review(comp, 0)
        assert new_ease >= MIN_EASE_FACTOR

    def test_passing_quality_uses_initial_intervals(self):
        """Quality >= 3 with few reviews uses an initial interval schedule."""
        comp = _make_competency(correct_count=0)  # first review
        next_review, _ = SpacedRepetitionService.calculate_next_review(comp, 4)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        delta_days = (next_review - now).total_seconds() / 86400
        # correct_count=0 → INITIAL_INTERVALS[0] = 1 day
        assert 0.9 < delta_days < 1.5
