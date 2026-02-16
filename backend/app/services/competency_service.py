import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import ConceptHierarchy, MasteryLevel, StudentCompetency, Topic

"""
Competency Service - Tracks student mastery of individual concepts.
Uses Exponentially Weighted Average (EWA) for mastery score updates.
"""

logger = logging.getLogger(__name__)

def _sanitize_for_log(value: Any) -> str:
    """
    Sanitize a value for safe logging by removing line breaks.

    This helps prevent log injection when logging user-controlled data.
    """
    text = str(value)
    # Remove common line break sequences
    return text.replace("\r\n", "").replace("\n", "").replace("\r", "")

# EWA learning rate
MASTERY_ALPHA = 0.3

# Mastery thresholds
MASTERY_THRESHOLDS = {
    MasteryLevel.MASTERED: 0.85,
    MasteryLevel.PROFICIENT: 0.60,
    MasteryLevel.DEVELOPING: 0.30,
    MasteryLevel.NOVICE: 0.0,
}

# Minimum attempts before earning higher levels
MIN_ATTEMPTS_FOR_PROFICIENT = 3
MIN_ATTEMPTS_FOR_MASTERED = 5

# Topic -> taxonomy filename mapping
TOPIC_TAXONOMY_FILES = {
    "linear_programming": "linear_programming.json",
    "mathematical_modeling": "mathematical_modeling.json",
    "integer_programming": "integer_programming.json",
}


# ---------------------------------------------------------------------------
# Concept Taxonomy Registry (singleton)
# ---------------------------------------------------------------------------

_taxonomy_registry: "ConceptTaxonomyRegistry | None" = None


class ConceptTaxonomyRegistry:
    """Loads and caches concept taxonomy JSON files."""

    def __init__(self, taxonomies_path: str):
        self.taxonomies_path = taxonomies_path
        self._taxonomies: dict[str, dict[str, Any]] = {}
        self._concepts_by_id: dict[str, dict[str, Any]] = {}
        self._load_all()

    def _load_all(self) -> None:
        for topic, filename in TOPIC_TAXONOMY_FILES.items():
            path = os.path.join(self.taxonomies_path, filename)
            if not os.path.exists(path):
                logger.warning(f"Taxonomy file not found: {path}")
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                self._taxonomies[topic] = data
                for concept in data.get("concepts", []):
                    self._concepts_by_id[concept["concept_id"]] = concept
                logger.info(f"Loaded {len(data.get('concepts', []))} concepts for {topic}")
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Error loading taxonomy {path}: {e}")

    def get_concepts_for_topic(self, topic: str) -> list[dict[str, Any]]:
        return self._taxonomies.get(topic, {}).get("concepts", [])

    def get_concept(self, concept_id: str) -> dict[str, Any] | None:
        return self._concepts_by_id.get(concept_id)

    def concept_exists(self, concept_id: str) -> bool:
        return concept_id in self._concepts_by_id

    def get_all_concept_ids(self) -> list[str]:
        return list(self._concepts_by_id.keys())


def get_taxonomy_registry() -> ConceptTaxonomyRegistry:
    global _taxonomy_registry
    if _taxonomy_registry is None:
        taxonomies_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "data", "concept_taxonomies"
        )
        _taxonomy_registry = ConceptTaxonomyRegistry(taxonomies_path)
    return _taxonomy_registry


# ---------------------------------------------------------------------------
# Competency Service
# ---------------------------------------------------------------------------

class CompetencyService:
    """Service for tracking and updating student concept mastery."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # DB seeding
    # ------------------------------------------------------------------

    def seed_concept_hierarchy(self) -> int:
        """
        Idempotently populate ConceptHierarchy from taxonomy JSON files.
        Returns number of new concepts inserted.
        """
        registry = get_taxonomy_registry()
        inserted = 0

        for topic_str in TOPIC_TAXONOMY_FILES:
            try:
                topic_enum = Topic(topic_str)
            except ValueError:
                logger.warning(f"Unknown topic in taxonomy: {topic_str}")
                continue

            concepts = registry.get_concepts_for_topic(topic_str)
            for concept in concepts:
                existing = self.db.query(ConceptHierarchy).filter(
                    ConceptHierarchy.concept_id == concept["concept_id"]
                ).first()

                if existing:
                    continue

                node = ConceptHierarchy(
                    concept_id=concept["concept_id"],
                    concept_name=concept["name"],
                    topic=topic_enum,
                    parent_concept_id=None,
                    bloom_level=concept["bloom_level"],
                    prerequisites=concept.get("prerequisites", []),
                )
                self.db.add(node)
                inserted += 1

        try:
            self.db.commit()
            logger.info(f"Seeded {inserted} concept hierarchy entries")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error seeding concept hierarchy: {e}")

        return inserted

    # ------------------------------------------------------------------
    # Core competency operations
    # ------------------------------------------------------------------

    def update_competency(
        self,
        student_id: int,
        concept_id: str,
        is_correct: bool,
        performance_score: float,
    ) -> StudentCompetency:
        """
        Update (or create) a student's mastery record for a concept.
        Uses EWA to update mastery_score.

        Args:
            student_id: Student ID
            concept_id: Concept ID (e.g., "lp.simplex.method")
            is_correct: Whether this attempt was successful
            performance_score: Normalized score 0.0-1.0 for this attempt

        Returns:
            Updated StudentCompetency object
        """
        now = datetime.now(timezone.utc)

        competency = self.db.query(StudentCompetency).filter(
            StudentCompetency.student_id == student_id,
            StudentCompetency.concept_id == concept_id,
        ).first()

        if competency is None:
            concept_node = self.db.query(ConceptHierarchy).filter(
                ConceptHierarchy.concept_id == concept_id
            ).first()

            concept_name = concept_node.concept_name if concept_node else concept_id
            topic = concept_node.topic if concept_node else Topic.OPERATIONS_RESEARCH

            competency = StudentCompetency(
                student_id=student_id,
                topic=topic,
                concept_id=concept_id,
                concept_name=concept_name,
                mastery_level=MasteryLevel.NOVICE,
                mastery_score=0.0,
                attempts_count=0,
                correct_count=0,
                decay_factor=2.5,
            )
            self.db.add(competency)

        # Update counters
        competency.attempts_count += 1
        competency.last_attempt_at = now

        if is_correct:
            competency.correct_count += 1
            competency.last_correct_at = now

        # EWA update
        if competency.attempts_count == 1:
            competency.mastery_score = float(performance_score)
        else:
            competency.mastery_score = (
                MASTERY_ALPHA * performance_score
                + (1 - MASTERY_ALPHA) * competency.mastery_score
            )

        # Clamp to [0, 1]
        competency.mastery_score = max(0.0, min(1.0, competency.mastery_score))

        # Recalculate mastery level
        competency.mastery_level = self.calculate_mastery_level(
            competency.mastery_score, competency.attempts_count
        )

        try:
            self.db.commit()
            self.db.refresh(competency)
        except IntegrityError:
            self.db.rollback()
            competency = self.db.query(StudentCompetency).filter(
                StudentCompetency.student_id == student_id,
                StudentCompetency.concept_id == concept_id,
            ).first()

        logger.info(
            f"Updated competency: student={student_id}, concept={concept_id}, "
            f"score={competency.mastery_score:.2f}, level={competency.mastery_level.value}"
        )
        return competency

    @staticmethod
    def calculate_mastery_level(mastery_score: float, attempts_count: int) -> MasteryLevel:
        """
        Derive MasteryLevel from score and attempt count.
        Requires minimum attempts to reach higher levels.
        """
        if attempts_count == 0:
            return MasteryLevel.NOT_STARTED

        if mastery_score >= 0.85 and attempts_count >= MIN_ATTEMPTS_FOR_MASTERED:
            return MasteryLevel.MASTERED
        if mastery_score >= 0.60 and attempts_count >= MIN_ATTEMPTS_FOR_PROFICIENT:
            return MasteryLevel.PROFICIENT
        if mastery_score >= 0.30:
            return MasteryLevel.DEVELOPING
        return MasteryLevel.NOVICE

    def get_student_competencies(
        self, student_id: int, topic: str
    ) -> list[StudentCompetency]:
        """Get all competency records for a student in a topic."""
        try:
            topic_enum = Topic(topic)
        except ValueError:
            safe_topic = _sanitize_for_log(topic)
            logger.warning(f"Unknown topic: {safe_topic}")
            return []

        return self.db.query(StudentCompetency).filter(
            StudentCompetency.student_id == student_id,
            StudentCompetency.topic == topic_enum,
        ).all()

    def get_mastery_summary(self, student_id: int, topic: str) -> dict[str, Any]:
        """
        Summarize mastery levels across all concepts in a topic.
        Includes NOT_STARTED for concepts the student hasn't encountered yet.
        """
        competencies = self.get_student_competencies(student_id, topic)

        registry = get_taxonomy_registry()
        all_concepts = {c["concept_id"]: c for c in registry.get_concepts_for_topic(topic)}

        level_counts = {level.value: 0 for level in MasteryLevel}
        concept_details = []

        known_ids = set()
        for comp in competencies:
            level_counts[comp.mastery_level.value] += 1
            known_ids.add(comp.concept_id)
            concept_details.append({
                "concept_id": comp.concept_id,
                "concept_name": comp.concept_name,
                "mastery_level": comp.mastery_level.value,
                "mastery_score": round(comp.mastery_score, 3),
                "attempts_count": comp.attempts_count,
            })

        for cid, c in all_concepts.items():
            if cid not in known_ids:
                level_counts[MasteryLevel.NOT_STARTED.value] += 1
                concept_details.append({
                    "concept_id": cid,
                    "concept_name": c["name"],
                    "mastery_level": MasteryLevel.NOT_STARTED.value,
                    "mastery_score": 0.0,
                    "attempts_count": 0,
                })

        avg_score = (
            sum(c["mastery_score"] for c in concept_details) / len(concept_details)
            if concept_details else 0.0
        )

        return {
            "student_id": student_id,
            "topic": topic,
            "total_concepts": len(concept_details),
            "level_counts": level_counts,
            "average_mastery_score": round(avg_score, 3),
            "concepts": concept_details,
        }

    def get_next_concepts_to_learn(
        self, student_id: int, topic: str
    ) -> list[dict[str, Any]]:
        """
        Return concepts recommended for the student to study next.
        Logic: concepts whose prerequisites are all PROFICIENT or MASTERED,
        and which the student hasn't MASTERED yet. Limit to 5.
        """
        competencies = self.get_student_competencies(student_id, topic)
        mastered_or_proficient = {
            c.concept_id
            for c in competencies
            if c.mastery_level in (MasteryLevel.PROFICIENT, MasteryLevel.MASTERED)
        }
        all_competencies = {c.concept_id: c for c in competencies}

        registry = get_taxonomy_registry()
        all_concepts = registry.get_concepts_for_topic(topic)

        recommendations = []
        for concept in all_concepts:
            cid = concept["concept_id"]

            if cid in mastered_or_proficient:
                continue

            prereqs = concept.get("prerequisites", [])
            if all(p in mastered_or_proficient for p in prereqs):
                comp = all_competencies.get(cid)
                recommendations.append({
                    "concept_id": cid,
                    "concept_name": concept["name"],
                    "bloom_level": concept["bloom_level"],
                    "current_mastery_score": round(comp.mastery_score, 3) if comp else 0.0,
                    "current_mastery_level": comp.mastery_level.value if comp else MasteryLevel.NOT_STARTED.value,
                    "prerequisites": prereqs,
                })

        bloom_order = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        recommendations.sort(
            key=lambda c: (
                bloom_order.index(c["bloom_level"]) if c["bloom_level"] in bloom_order else 99,
                c["current_mastery_score"],
            )
        )
        return recommendations[:5]


def get_competency_service(db: Session) -> CompetencyService:
    return CompetencyService(db)
