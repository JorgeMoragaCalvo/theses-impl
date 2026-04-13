"""
Unit tests for BKT (Bayesian Knowledge Tracing) — verifies math against
hand-computed reference values using default parameters:
  P(L0)=0.1, P(T)=0.3, P(G)=0.25, P(S)=0.1
"""

import pytest

from app.services.bkt_service import (
    DEFAULT_P_G,
    DEFAULT_P_L0,
    DEFAULT_P_S,
    DEFAULT_P_T,
    BKTService,
    bkt_update,
)


# ---------------------------------------------------------------------------
# Hand-computed reference values
# ---------------------------------------------------------------------------
# All derivations use: P(T)=0.3, P(G)=0.25, P(S)=0.1
#
# Formula:
#   p_obs_know    = (1-P(S)) if correct else P(S)
#   p_obs_not_know = P(G)    if correct else (1-P(G))
#   p_obs         = p_obs_know * p_learn + p_obs_not_know * (1 - p_learn)
#   posterior     = p_obs_know * p_learn / p_obs
#   p_next        = posterior + (1 - posterior) * P(T)


class TestBktUpdateCorrect:
    """Correct answer observations."""

    def test_correct_from_prior(self):
        # p_learn = 0.1 (prior), correct answer
        # p_obs_know=0.9, p_obs_not_know=0.25
        # p_obs = 0.9*0.1 + 0.25*0.9 = 0.09 + 0.225 = 0.315
        # posterior = 0.09 / 0.315 = 0.285714...
        # p_next = 0.285714 + 0.714286*0.3 = 0.285714 + 0.214286 = 0.5
        result = bkt_update(DEFAULT_P_L0, is_correct=True)
        assert abs(result - 0.5) < 1e-6

    def test_correct_from_zero(self):
        # p_learn = 0.0, correct answer
        # posterior = 0.0 (no prior knowledge mass)
        # p_next = 0.0 + 1.0 * 0.3 = 0.3
        result = bkt_update(0.0, is_correct=True)
        assert abs(result - 0.3) < 1e-6

    def test_correct_from_one(self):
        # p_learn = 1.0, correct answer → stays at 1.0
        result = bkt_update(1.0, is_correct=True)
        assert abs(result - 1.0) < 1e-6

    def test_correct_from_half(self):
        # p_learn = 0.5, correct answer
        # p_obs = 0.9*0.5 + 0.25*0.5 = 0.45 + 0.125 = 0.575
        # posterior = 0.45 / 0.575 = 0.782609...
        # p_next = 0.782609 + 0.217391*0.3 = 0.782609 + 0.065217 = 0.847826...
        result = bkt_update(0.5, is_correct=True)
        assert abs(result - 0.847826) < 1e-5


class TestBktUpdateIncorrect:
    """Incorrect answer observations."""

    def test_incorrect_from_prior(self):
        # p_learn = 0.1, incorrect answer
        # p_obs_know=0.1 (slip), p_obs_not_know=0.75
        # p_obs = 0.1*0.1 + 0.75*0.9 = 0.01 + 0.675 = 0.685
        # posterior = 0.01 / 0.685 = 0.014599...
        # p_next = 0.014599 + 0.985401*0.3 = 0.014599 + 0.295620 = 0.310219...
        result = bkt_update(DEFAULT_P_L0, is_correct=False)
        assert abs(result - 0.310219) < 1e-5

    def test_incorrect_from_zero(self):
        # p_learn = 0.0, incorrect
        # posterior = 0.0
        # p_next = 0.0 + 1.0 * 0.3 = 0.3
        result = bkt_update(0.0, is_correct=False)
        assert abs(result - 0.3) < 1e-6

    def test_incorrect_from_one(self):
        # p_learn = 1.0, incorrect (must be a slip)
        # p_obs_know=0.1, p_obs_not_know=0.75
        # p_obs = 0.1*1.0 + 0.75*0.0 = 0.1
        # posterior = 0.1 / 0.1 = 1.0
        # p_next = 1.0 + 0.0 * 0.3 = 1.0
        result = bkt_update(1.0, is_correct=False)
        assert abs(result - 1.0) < 1e-6


class TestBktMonotonicity:
    """Repeated correct answers must increase P(L_n) monotonically."""

    def test_consecutive_correct_increases(self):
        p = DEFAULT_P_L0
        prev = p
        for _ in range(10):
            p = bkt_update(p, is_correct=True)
            assert p > prev
            prev = p

    def test_converges_toward_one_on_correct_streak(self):
        p = DEFAULT_P_L0
        for _ in range(30):
            p = bkt_update(p, is_correct=True)
        assert p > 0.95

    def test_output_always_in_unit_interval(self):
        for p_init in [0.0, 0.1, 0.5, 0.9, 1.0]:
            for correct in [True, False]:
                result = bkt_update(p_init, is_correct=correct)
                assert 0.0 <= result <= 1.0, f"Out of [0,1]: p_init={p_init}, correct={correct} → {result}"


class TestBktServiceOrm:
    """BKTService.update() on a mock StudentCompetency-like object."""

    class _FakeCompetency:
        def __init__(self, bkt_p_learn=None):
            self.bkt_p_learn = bkt_p_learn

    def test_initialises_from_p_l0_when_null(self):
        comp = self._FakeCompetency(bkt_p_learn=None)
        svc = BKTService()
        result = svc.update(comp, is_correct=True)
        # Should initialise from DEFAULT_P_L0=0.1 then apply one correct update → 0.5
        assert abs(result - 0.5) < 1e-6
        assert abs(comp.bkt_p_learn - 0.5) < 1e-6

    def test_uses_existing_value_when_set(self):
        comp = self._FakeCompetency(bkt_p_learn=0.5)
        svc = BKTService()
        result = svc.update(comp, is_correct=True)
        expected = bkt_update(0.5, is_correct=True)
        assert abs(result - expected) < 1e-9
        assert abs(comp.bkt_p_learn - expected) < 1e-9

    def test_mutates_competency_in_place(self):
        comp = self._FakeCompetency(bkt_p_learn=0.2)
        svc = BKTService()
        svc.update(comp, is_correct=False)
        assert comp.bkt_p_learn != 0.2  # must have changed

    def test_get_p_learn_fallback(self):
        comp = self._FakeCompetency(bkt_p_learn=None)
        assert BKTService.get_p_learn(comp) == DEFAULT_P_L0

    def test_get_p_learn_existing(self):
        comp = self._FakeCompetency(bkt_p_learn=0.7)
        assert BKTService.get_p_learn(comp) == 0.7