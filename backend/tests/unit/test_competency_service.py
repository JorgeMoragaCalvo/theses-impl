"""
Unit tests for CompetencyService — EWA mastery calculation (needs test_db).
"""

from app.enums import MasteryLevel
from app.services.competency_service import (
    MASTERY_ALPHA,
    MIN_ATTEMPTS_FOR_MASTERED,
    MIN_ATTEMPTS_FOR_PROFICIENT,
    CompetencyService,
)


class TestMasteryLevel:
    def test_mastery_level_thresholds(self):
        calc = CompetencyService.calculate_mastery_level
        assert calc(0.0, 0) == MasteryLevel.NOT_STARTED
        assert calc(0.1, 1) == MasteryLevel.NOVICE
        assert calc(0.4, 2) == MasteryLevel.DEVELOPING
        assert calc(0.7, MIN_ATTEMPTS_FOR_PROFICIENT) == MasteryLevel.PROFICIENT
        assert calc(0.9, MIN_ATTEMPTS_FOR_MASTERED) == MasteryLevel.MASTERED


class TestUpdateCompetency:
    def test_creates_new_competency(self, test_db):
        """The first attempt on a concept creates a new record."""
        svc = CompetencyService(test_db)
        # Need a student
        from app.auth import get_password_hash
        from app.database import Student
        from app.enums import UserRole

        student = Student(
            name="Comp Student",
            email="comp@usach.cl",
            password_hash=get_password_hash("pass12345678"),
            role=UserRole.USER,
            is_active=True,
        )
        test_db.add(student)
        test_db.commit()
        test_db.refresh(student)

        comp = svc.update_competency(
            student_id=student.id,
            concept_id="lp.simplex.method",
            is_correct=True,
            performance_score=0.8,
        )
        assert comp is not None
        assert comp.concept_id == "lp.simplex.method"
        assert comp.attempts_count == 1
        assert comp.mastery_score == 0.8

    def test_ewa_formula(self, test_db):
        """Verify EWA: new = ALPHA * perf + (1 - ALPHA) * old."""
        svc = CompetencyService(test_db)
        from app.auth import get_password_hash
        from app.database import Student
        from app.enums import UserRole

        student = Student(
            name="EWA Student",
            email="ewa@usach.cl",
            password_hash=get_password_hash("pass12345678"),
            role=UserRole.USER,
            is_active=True,
        )
        test_db.add(student)
        test_db.commit()
        test_db.refresh(student)

        # The first attempt sets the score directly
        svc.update_competency(student.id, "lp.dual", True, 0.6)
        # The second attempt uses EWA
        comp = svc.update_competency(student.id, "lp.dual", True, 1.0)
        expected = MASTERY_ALPHA * 1.0 + (1 - MASTERY_ALPHA) * 0.6
        assert abs(comp.mastery_score - expected) < 0.01

    def test_min_attempts_guard(self, test_db):
        """High score with too few attempts should NOT reach MASTERED."""
        svc = CompetencyService(test_db)
        from app.auth import get_password_hash
        from app.database import Student
        from app.enums import UserRole

        student = Student(
            name="Guard Student",
            email="guard@usach.cl",
            password_hash=get_password_hash("pass12345678"),
            role=UserRole.USER,
            is_active=True,
        )
        test_db.add(student)
        test_db.commit()
        test_db.refresh(student)

        # One attempt with a perfect score
        comp = svc.update_competency(student.id, "lp.basis", True, 1.0)
        assert comp.mastery_level != MasteryLevel.MASTERED
