"""
Bayesian Knowledge Tracing (BKT) Service.

Implements the standard 4-parameter BKT Hidden Markov Model for knowledge modeling.
Replaces the EWA mastery score update with a probabilistic posterior estimate.

Parameters per concept (defaults used when no fitted values are available):
  P(L0) — prior probability a student already knows the concept
  P(T)  — probability of learning on each opportunity (transition)
  P(G)  — probability of guessing correctly without knowing
  P(S)  — probability of slipping (incorrect despite knowing)
"""

from ..database import StudentCompetency

# Default BKT parameters (conservative priors)
DEFAULT_P_L0: float = 0.1  # Low prior — assume student doesn't know concept yet
DEFAULT_P_T: float = 0.3  # Moderate learning rate per attempt
DEFAULT_P_G: float = 0.25  # Guess probability (1-in-4 chance)
DEFAULT_P_S: float = 0.1  # Low slip probability


def bkt_update(
    p_learn: float,
    is_correct: bool,
    p_t: float = DEFAULT_P_T,
    p_g: float = DEFAULT_P_G,
    p_s: float = DEFAULT_P_S,
) -> float:
    """
    BKT forward pass: compute P(L_{n+1}) given one observation.

    Steps:
      1. Compute likelihood of the observed answer given each latent state.
      2. Apply Bayes' rule to get the posterior P(L_n | observation).
      3. Apply the learning transition to get P(L_{n+1}).

    Args:
        p_learn:    Current P(L_n) — probability student knows the concept.
        is_correct: Whether the student answered correctly.
        p_t:        Learning rate (transition probability).
        p_g:        Guess probability (correct answer without knowledge).
        p_s:        Slip probability (incorrect answer despite knowledge).

    Returns:
        Updated P(L_{n+1}) clamped to [0, 1].
    """
    # Likelihood of the observation given each knowledge state
    if is_correct:
        p_obs_given_know = 1.0 - p_s  # knew it and didn't slip
        p_obs_given_not_know = p_g  # didn't know but guessed right
    else:
        p_obs_given_know = p_s  # knew it but slipped
        p_obs_given_not_know = 1.0 - p_g  # didn't know and didn't guess correctly

    # Total probability of this observation (normalising constant)
    p_obs = p_obs_given_know * p_learn + p_obs_given_not_know * (1.0 - p_learn)

    if p_obs <= 0.0:
        # Degenerate case — parameters produce zero-probability observation; no update
        return p_learn

    # Posterior: P(L_n | observation) via Bayes
    p_posterior = (p_obs_given_know * p_learn) / p_obs

    # Learning transition: P(L_{n+1}) = P(L_n|obs) + (1 - P(L_n|obs)) * P(T)
    p_next = p_posterior + (1.0 - p_posterior) * p_t

    return max(0.0, min(1.0, p_next))


class BKTService:
    """
    Wraps bkt_update() to operate on StudentCompetency ORM objects.

    Does not commit to the database — the caller (CompetencyService) owns the
    transaction.
    """

    def update(self, competency: StudentCompetency, is_correct: bool) -> float:
        """
        Update the BKT estimate stored in competency.bkt_p_learn.

        If bkt_p_learn is NULL (first-ever update), initialises to P(L0) before
        applying the forward pass.

        Args:
            competency: The StudentCompetency ORM instance to update (mutated in place).
            is_correct: Whether the current attempt was correct.

        Returns:
            The new P(L_{n+1}) value written to competency.bkt_p_learn.
        """
        current = competency.bkt_p_learn
        if current is None:
            current = DEFAULT_P_L0

        updated = bkt_update(current, is_correct)
        competency.bkt_p_learn = updated
        return updated

    @staticmethod
    def get_p_learn(competency: StudentCompetency) -> float:
        """Return current BKT estimate, falling back to P(L0) if not yet set."""
        if competency.bkt_p_learn is None:
            return DEFAULT_P_L0
        return float(competency.bkt_p_learn)
