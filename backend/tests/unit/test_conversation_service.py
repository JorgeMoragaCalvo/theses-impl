"""
Unit tests for ConversationService.compute_student_progress (needs test_db).
"""
from app.auth import get_password_hash
from app.database import Assessment, Conversation, Message, Student
from app.enums import Topic, UserRole
from app.services.conversation_service import ConversationService


class TestComputeStudentProgress:

    @staticmethod
    def _create_student(test_db, email="progress@usach.cl"):
        student = Student(
            name="Progress Student",
            email=email,
            password_hash=get_password_hash("pass12345678"),
            role=UserRole.USER,
            is_active=True,
            knowledge_levels={
                "operations_research": "beginner",
                "mathematical_modeling": "beginner",
                "linear_programming": "beginner",
                "integer_programming": "beginner",
                "nonlinear_programming": "beginner",
            },
        )
        test_db.add(student)
        test_db.commit()
        test_db.refresh(student)
        return student

    def test_compute_progress_no_data(self, test_db):
        """Brand-new student has zeroes for all progress metrics."""
        student = self._create_student(test_db, "nodata@usach.cl")
        svc = ConversationService(test_db)
        progress = svc.compute_student_progress(student.id)
        assert progress.total_conversations == 0
        assert progress.total_messages == 0
        assert progress.total_assessments == 0

    def test_compute_progress_with_data(self, test_db):
        """Progress reflects conversations and assessments correctly."""
        student = self._create_student(test_db, "withdata@usach.cl")
        svc = ConversationService(test_db)

        # Create a conversation with messages
        conv = Conversation(
            student_id=student.id,
            topic=Topic.LINEAR_PROGRAMMING,
        )
        test_db.add(conv)
        test_db.commit()
        test_db.refresh(conv)

        msg1 = Message(conversation_id=conv.id, role="user", content="Hello")
        msg2 = Message(conversation_id=conv.id, role="assistant", content="Hi!")
        test_db.add_all([msg1, msg2])

        # Create an assessment
        assessment = Assessment(
            student_id=student.id,
            topic=Topic.LINEAR_PROGRAMMING,
            question="What is LP?",
            score=5.0,
            max_score=7.0,
        )
        test_db.add(assessment)
        test_db.commit()

        progress = svc.compute_student_progress(student.id)
        assert progress.total_conversations == 1
        assert progress.total_messages == 2
        assert progress.total_assessments == 1
