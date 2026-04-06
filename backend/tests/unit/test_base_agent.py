"""
Unit tests for BaseAgent methods — confusion detection, feedback, review context,
validation, preprocessing, and postprocessing.
"""

from unittest.mock import MagicMock, patch

from app.agents.base_agent import BaseAgent


class TestDetectStudentConfusion:
    def test_high_confusion_keyword(self):
        result = BaseAgent.detect_student_confusion("No entiendo nada de esto", [])
        assert result["detected"] is True
        assert result["level"] == "high"

    def test_medium_confusion_keyword(self):
        result = BaseAgent.detect_student_confusion(
            "Estoy confundido con el simplex", []
        )
        assert result["detected"] is True
        assert result["level"] == "medium"

    def test_low_confusion_keyword(self):
        result = BaseAgent.detect_student_confusion("Puedes explicar eso?", [])
        assert result["detected"] is True
        assert result["level"] == "low"

    def test_no_confusion(self):
        result = BaseAgent.detect_student_confusion("Explica la dualidad en LP", [])
        assert result["detected"] is False
        assert result["level"] == "none"

    def test_repeated_topic_escalates(self):
        history = [
            {"role": "user", "content": "explica simplex otra vez"},
            {"role": "assistant", "content": "El simplex es..."},
            {"role": "user", "content": "no entiendo simplex todavía"},
            {"role": "assistant", "content": "El simplex funciona así..."},
            {"role": "user", "content": "simplex de nuevo por favor"},
        ]
        result = BaseAgent.detect_student_confusion("simplex una vez más", history)
        assert result["detected"] is True


class TestShouldAddFeedbackRequest:
    def test_feedback_on_confusion(self):
        result = BaseAgent.should_add_feedback_request(
            response_text="Short answer.",
            conversation_history=[],
            context={},
            confusion_detected=True,
        )
        assert result is True

    def test_feedback_on_periodic(self):
        history = [
            {"role": "user", "content": "q1"},
            {"role": "assistant", "content": "a1"},
            {"role": "user", "content": "q2"},
            {"role": "assistant", "content": "a2"},
            {"role": "user", "content": "q3"},
            {"role": "assistant", "content": "a3"},
        ]
        result = BaseAgent.should_add_feedback_request(
            response_text="Short.",
            conversation_history=history,
            context={},
            confusion_detected=False,
        )
        assert result is True

    def test_no_feedback_short_convo(self):
        result = BaseAgent.should_add_feedback_request(
            response_text="Hi.",
            conversation_history=[],
            context={},
            confusion_detected=False,
        )
        assert result is False


class TestAddFeedbackRequestToResponse:
    def test_high_confusion_adds_alternatives(self):
        resp = BaseAgent.add_feedback_request_to_response("Answer here.", "high")
        assert "Answer here." in resp
        assert len(resp) > len("Answer here.")
        assert (
            "analogy" in resp.lower()
            or "example" in resp.lower()
            or "step" in resp.lower()
        )

    def test_medium_confusion(self):
        resp = BaseAgent.add_feedback_request_to_response("Answer.", "medium")
        assert len(resp) > len("Answer.")

    def test_low_confusion(self):
        resp = BaseAgent.add_feedback_request_to_response("Answer.", "low")
        assert len(resp) > len("Answer.")

    def test_no_confusion(self):
        resp = BaseAgent.add_feedback_request_to_response("Answer.", "none")
        assert len(resp) > len("Answer.")


class TestFormatReviewContext:
    def test_empty_reviews(self):
        assert BaseAgent.format_review_context([]) == ""

    def test_with_reviews(self):
        review = MagicMock()
        review.concept_name = "Simplex Method"
        review.mastery_score = 0.65
        review.mastery_level.value = "developing"
        result = BaseAgent.format_review_context([review])
        assert "Simplex Method" in result
        assert "65%" in result
        assert "SPACED REPETITION" in result

    def test_multiple_reviews(self):
        reviews = []
        for name in ["Simplex", "Duality"]:
            r = MagicMock()
            r.concept_name = name
            r.mastery_score = 0.5
            r.mastery_level.value = "developing"
            reviews.append(r)
        result = BaseAgent.format_review_context(reviews)
        assert "2 concept(s)" in result


class TestValidateMessage:
    def test_empty_message(self):
        assert BaseAgent.validate_message("") is False

    def test_whitespace_only(self):
        assert BaseAgent.validate_message("   ") is False

    def test_too_long(self):
        assert BaseAgent.validate_message("a" * 1001) is False

    def test_valid_message(self):
        assert BaseAgent.validate_message("How does simplex work?") is True

    def test_boundary_length(self):
        assert BaseAgent.validate_message("a" * 1000) is True


class TestPreprocessMessage:
    def test_strips_whitespace(self):
        assert BaseAgent.preprocess_message("  hello  ") == "hello"

    def test_collapses_spaces(self):
        assert BaseAgent.preprocess_message("hello    world") == "hello world"


class TestPostprocessResponse:
    def test_strips_response(self):
        assert BaseAgent.postprocess_response("  answer  ") == "answer"


class TestSanitizeForLog:
    def test_removes_newlines(self):
        result = BaseAgent._sanitize_for_log("line1\nline2\rline3")
        assert "\n" not in result
        assert "\r" not in result

    def test_non_string(self):
        result = BaseAgent._sanitize_for_log(42)
        assert result == "42"


class TestBuildEnhancedSystemPrompt:
    def test_with_adaptive(self):
        agent = MagicMock(spec=BaseAgent)
        agent.format_review_context = BaseAgent.format_review_context
        prompt = BaseAgent.build_enhanced_system_prompt(
            agent, "base prompt", "adaptive section", {"due_reviews": []}
        )
        assert "base prompt" in prompt
        assert "adaptive section" in prompt

    def test_without_adaptive(self):
        agent = MagicMock(spec=BaseAgent)
        agent.format_review_context = BaseAgent.format_review_context
        prompt = BaseAgent.build_enhanced_system_prompt(
            agent, "base prompt", "", {"due_reviews": []}
        )
        assert prompt == "base prompt"

    def test_with_reviews(self):
        review = MagicMock()
        review.concept_name = "Duality"
        review.mastery_score = 0.4
        review.mastery_level.value = "novice"
        agent = MagicMock(spec=BaseAgent)
        agent.format_review_context = BaseAgent.format_review_context
        prompt = BaseAgent.build_enhanced_system_prompt(
            agent, "base", "", {"due_reviews": [review]}
        )
        assert "Duality" in prompt


class TestGetSystemPrompt:
    def test_builds_prompt_from_concrete_agent(self):
        """Use IntegerProgrammingAgent as a concrete subclass to test get_system_prompt."""
        from app.agents.integer_programming_agent import IntegerProgrammingAgent

        with patch("app.agents.base_agent.get_llm_service"):
            agent = IntegerProgrammingAgent()
        context = {
            "student": {"knowledge_level": "beginner", "student_name": "Juan"},
        }
        prompt = agent.get_system_prompt(context)
        assert "Juan" in prompt
        assert "PRINCIPIANTE" in prompt

    def test_advanced_level(self):
        from app.agents.integer_programming_agent import IntegerProgrammingAgent

        with patch("app.agents.base_agent.get_llm_service"):
            agent = IntegerProgrammingAgent()
        context = {
            "student": {"knowledge_level": "advanced", "student_name": "Ana"},
        }
        prompt = agent.get_system_prompt(context)
        assert "AVANZADO" in prompt

    def test_unknown_level_defaults_beginner(self):
        from app.agents.integer_programming_agent import IntegerProgrammingAgent

        with patch("app.agents.base_agent.get_llm_service"):
            agent = IntegerProgrammingAgent()
        context = {
            "student": {"knowledge_level": "expert", "student_name": "X"},
        }
        prompt = agent.get_system_prompt(context)
        assert "PRINCIPIANTE" in prompt


class TestLoadCourseMaterials:
    def test_load_nonexistent_file(self):
        from app.agents.integer_programming_agent import IntegerProgrammingAgent

        with patch("app.agents.base_agent.get_llm_service"):
            agent = IntegerProgrammingAgent()
        result = agent.load_course_materials("/nonexistent/path.md")
        assert result is False
        assert agent.course_materials is None


class TestGetAgentInfo:
    def test_returns_info_dict(self):
        from app.agents.integer_programming_agent import IntegerProgrammingAgent

        with patch("app.agents.base_agent.get_llm_service"):
            agent = IntegerProgrammingAgent()
        info = agent.get_agent_info()
        assert info["name"] == "Tutor de Programación Entera"
        assert info["type"] == "integer_programming"
        assert "has_course_materials" in info


class TestFormatContextForPrompt:
    def test_with_knowledge_level(self):
        from app.agents.integer_programming_agent import IntegerProgrammingAgent

        with patch("app.agents.base_agent.get_llm_service"):
            agent = IntegerProgrammingAgent()
        context = {
            "student": {
                "knowledge_level": "beginner",
                "knowledge_level_description": "New to the topic",
            }
        }
        result = agent.format_context_for_prompt(context)
        assert "BEGINNER" in result
        assert "New to the topic" in result


class TestBuildAdaptivePromptSectionExtended:
    def test_repeated_topic_section(self):
        analysis = {
            "detected": True,
            "level": "low",
            "signals": [],
            "repeated_topic": {"repeated": True, "topic": "simplex", "count": 3},
        }
        result = BaseAgent.build_adaptive_prompt_section(analysis, "step-by-step")
        assert "simplex" in result
        assert "DIFFERENT" in result.upper() or "DIFERENTE" in result.upper()

    def test_strategy_instructions_included(self):
        analysis = {"detected": False, "level": "none", "signals": []}
        result = BaseAgent.build_adaptive_prompt_section(analysis, "visual")
        assert "VISUAL" in result

    def test_unknown_strategy_no_crash(self):
        analysis = {"detected": False, "level": "none", "signals": []}
        result = BaseAgent.build_adaptive_prompt_section(analysis, "unknown-strategy")
        # Should not raise, may be empty or minimal
        assert isinstance(result, str)

    def test_medium_confusion_section(self):
        analysis = {
            "detected": True,
            "level": "medium",
            "signals": ["medium:confundido"],
        }
        result = BaseAgent.build_adaptive_prompt_section(analysis, "example-based")
        assert "ADAPTIVE" in result or "NOTICE" in result

    def test_low_confusion_section(self):
        analysis = {"detected": True, "level": "low", "signals": ["low:espera"]}
        result = BaseAgent.build_adaptive_prompt_section(analysis, "conceptual")
        assert (
            "NOTE" in result
            or "clarification" in result.lower()
            or "ADAPTIVE" in result
        )
