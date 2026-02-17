"""
Exercise Progress Service - Tracks student completion and enforces per-topic progression gating.

Students must solve exercises in rank order within each topic.
Rank 1 exercises are always unlocked. Rank 0 (no metadata) exercises are always unlocked.
"Solving" means achieving >= 50% of max_score.
"""

import logging
from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..database import Assessment, Topic
from .exercise_assessment_service import get_exercise_registry

logger = logging.getLogger(__name__)


def get_completed_exercise_ids(db: Session, student_id: int, topic: Topic) -> set[str]:
    """
    Query assessments for exercise_ids the student has completed (score >= 50% of max_score).

    Filters by extra_data->>'source' IN ('exercise', 'exercise_similar') and matching topic.
    """
    assessments = (
        db.query(Assessment)
        .filter(
            and_(
                Assessment.student_id == student_id,
                Assessment.topic == topic,
                Assessment.graded_at.isnot(None),
            )
        )
        .all()
    )

    completed = set()
    for a in assessments:
        extra = a.extra_data or {}
        source = extra.get("source", "")
        if source not in ("exercise", "exercise_similar"):
            continue
        if a.score is not None and a.max_score and a.score >= a.max_score * 0.5:
            exercise_id = extra.get("exercise_id")
            if exercise_id:
                completed.add(exercise_id)

    return completed


def compute_max_unlocked_rank(completed_ids: set[str], exercises: list[dict[str, Any]]) -> int:
    """
    Compute the maximum unlocked rank for a list of exercises within one topic.

    Starting from rank 1 (always unlocked), check each rank sequentially.
    If any exercise at rank N is completed, rank N+1 is unlocked.
    Stop at the first rank where no exercise is completed.
    """
    # Build a mapping: rank -> list of exercise ids at that rank
    rank_exercises: dict[int, list[str]] = {}
    max_rank = 0
    for ex in exercises:
        rank = ex.get("rank", 0)
        if rank == 0:
            continue
        rank_exercises.setdefault(rank, []).append(ex["id"])
        max_rank = max(max_rank, rank)

    if max_rank == 0:
        return 0  # No ranked exercises

    # Rank 1 is always unlocked; check from rank 1 upward
    unlocked = 1
    # Iterates ranks; updates unlocked rank if any exercise completed
    for rank in range(1, max_rank + 1):
        ids_at_rank = rank_exercises.get(rank, [])
        if any(eid in completed_ids for eid in ids_at_rank):
            unlocked = rank + 1
        else:
            break

    return unlocked


def get_exercises_with_progress(
    db: Session, student_id: int, topic: Topic | None = None
) -> list[dict[str, Any]]:
    """
    Return exercises enriched with `locked` and `completed` fields.

    Groups by topic for per-topic gating. If a topic is provided, filters to that topic only.
    """
    registry = get_exercise_registry()

    if topic:
        topics = [topic]
    else:
        topics = registry.get_topics_with_exercises()

    result = []
    for t in topics:
        exercises = registry.list_exercises_by_topic(t)
        if not exercises:
            continue

        completed_ids = get_completed_exercise_ids(db, student_id, t)
        max_unlocked = compute_max_unlocked_rank(completed_ids, exercises)

        for ex in exercises:
            ex_copy = ex.copy()
            rank = ex_copy.get("rank", 0)
            ex_copy["completed"] = ex_copy["id"] in completed_ids

            if rank == 0:
                # No metadata / unranked exercises are always unlocked
                ex_copy["locked"] = False
            else:
                ex_copy["locked"] = rank > max_unlocked

            result.append(ex_copy)

    return result
