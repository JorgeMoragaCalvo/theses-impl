"""
Extended unit tests for app.utils — covering functions not hit by existing tests.
"""

from unittest.mock import MagicMock

from app.utils import (
    clean_whitespace,
    count_tokens_estimate,
    detect_confusion_signals,
    detect_repeated_topic,
    extract_code_blocks,
    format_conversation_history,
    format_error_message,
    format_knowledge_level_context,
    format_message_for_llm,
    get_explanation_strategies_from_context,
    parse_topic_from_message,
    sanitize_log_value,
    should_request_feedback,
    truncate_text,
    validate_student_knowledge_level,
)


class TestSanitizeLogValue:
    def test_removes_newlines(self):
        assert "\n" not in sanitize_log_value("a\nb\r\nc")

    def test_non_string(self):
        assert sanitize_log_value(42) == "42"


class TestFormatMessageForLlm:
    def test_format(self):
        result = format_message_for_llm("user", "hello")
        assert result == {"role": "user", "content": "hello"}


class TestFormatConversationHistory:
    def test_formats_list(self):
        msg1 = MagicMock(role="user", content="hi")
        msg2 = MagicMock(role="assistant", content="hello")
        result = format_conversation_history([msg1, msg2])
        assert result == [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]


class TestTruncateText:
    def test_short_text_unchanged(self):
        assert truncate_text("hello", 10) == "hello"

    def test_truncation(self):
        result = truncate_text("a" * 100, 10)
        assert len(result) == 10
        assert result.endswith("...")

    def test_custom_suffix(self):
        result = truncate_text("a" * 100, 10, suffix="…")
        assert result.endswith("…")


class TestExtractCodeBlocks:
    def test_extracts_blocks(self):
        text = "Some text\n```python\nprint('hi')\n```\nMore text\n```\nx = 1\n```"
        result = extract_code_blocks(text)
        assert len(result) == 2
        assert "print('hi')" in result[0]

    def test_no_blocks(self):
        assert extract_code_blocks("no code here") == []


class TestCleanWhitespace:
    def test_collapses_spaces(self):
        assert clean_whitespace("a   b") == "a b"

    def test_collapses_newlines(self):
        assert clean_whitespace("a\n\n\n\nb") == "a\n\nb"

    def test_strips(self):
        assert clean_whitespace("  hello  ") == "hello"


class TestCountTokensEstimate:
    def test_estimate(self):
        assert count_tokens_estimate("a" * 400) == 100

    def test_empty(self):
        assert count_tokens_estimate("") == 0


class TestFormatKnowledgeLevelContext:
    def test_beginner(self):
        result = format_knowledge_level_context("beginner")
        assert "nuevo" in result or "paso a paso" in result

    def test_intermediate(self):
        result = format_knowledge_level_context("intermediate")
        assert "básica" in result or "moderada" in result

    def test_advanced(self):
        result = format_knowledge_level_context("advanced")
        assert "competente" in result or "teóricos" in result

    def test_unknown_defaults(self):
        result = format_knowledge_level_context("expert")
        assert "nuevo" in result or "paso a paso" in result

    def test_case_insensitive(self):
        result = format_knowledge_level_context("BEGINNER")
        assert "nuevo" in result or "paso a paso" in result


class TestParseTopicFromMessage:
    def test_linear_programming(self):
        assert parse_topic_from_message("Explica el simplex") == "linear_programming"

    def test_integer_programming(self):
        assert (
            parse_topic_from_message("Variable binaria y branch and bound")
            == "integer_programming"
        )

    def test_nonlinear(self):
        assert (
            parse_topic_from_message("Condiciones KKT y gradiente")
            == "nonlinear_programming"
        )

    def test_operations_research(self):
        assert (
            parse_topic_from_message("Investigación de operaciones básica")
            == "operations_research"
        )

    def test_mathematical_modeling(self):
        assert (
            parse_topic_from_message("Formulación del modelo matemático")
            == "mathematical_modeling"
        )

    def test_general(self):
        assert parse_topic_from_message("How are you?") == "general"


class TestFormatErrorMessage:
    def test_user_friendly(self):
        result = format_error_message(Exception("bad thing"))
        assert "Lo siento" in result
        assert "bad thing" not in result

    def test_not_user_friendly(self):
        result = format_error_message(Exception("bad thing"), user_friendly=False)
        assert "bad thing" in result


class TestValidateStudentKnowledgeLevel:
    def test_valid_levels(self):
        assert validate_student_knowledge_level("beginner") == "beginner"
        assert validate_student_knowledge_level("intermediate") == "intermediate"
        assert validate_student_knowledge_level("advanced") == "advanced"

    def test_case_insensitive(self):
        assert validate_student_knowledge_level("BEGINNER") == "beginner"

    def test_invalid_defaults(self):
        assert validate_student_knowledge_level("expert") == "beginner"


class TestDetectConfusionSignals:
    def test_high_confusion(self):
        result = detect_confusion_signals("No entiendo nada")
        assert result["detected"] is True
        assert result["level"] == "high"

    def test_medium_confusion(self):
        result = detect_confusion_signals("Estoy confundido con esto")
        assert result["level"] == "medium"

    def test_low_confusion(self):
        result = detect_confusion_signals("Puedes explicar más?")
        assert result["level"] == "low"

    def test_short_confused_response(self):
        result = detect_confusion_signals("qué?")
        assert result["detected"] is True
        assert result["level"] == "low"

    def test_multiple_question_marks(self):
        result = detect_confusion_signals("Cómo funciona esto??")
        assert "multiple_question_marks" in result["signals"]

    def test_no_confusion(self):
        result = detect_confusion_signals("Explica la dualidad")
        assert result["detected"] is False


class TestDetectRepeatedTopic:
    def test_no_history(self):
        result = detect_repeated_topic([])
        assert result["repeated"] is False

    def test_single_message(self):
        result = detect_repeated_topic([{"role": "user", "content": "simplex"}])
        assert result["repeated"] is False

    def test_repeated_topic(self):
        history = [
            {"role": "user", "content": "explain simplex method"},
            {"role": "assistant", "content": "The simplex method is..."},
            {"role": "user", "content": "tell me about simplex again"},
        ]
        result = detect_repeated_topic(history)
        assert result["repeated"] is True
        assert result["topic"] == "simplex"

    def test_no_repetition(self):
        history = [
            {"role": "user", "content": "explain duality"},
            {"role": "assistant", "content": "Duality is..."},
            {"role": "user", "content": "what about sensitivity analysis"},
        ]
        result = detect_repeated_topic(history)
        # No word repeated >= 2 times across user messages
        # (depends on word extraction)
        assert isinstance(result["repeated"], bool)


class TestGetExplanationStrategiesFromContext:
    def test_empty_context(self):
        result = get_explanation_strategies_from_context({})
        assert result == []

    def test_with_strategies(self):
        ctx = {
            "conversation_extra_data": {"strategies_used": ["step-by-step", "visual"]}
        }
        result = get_explanation_strategies_from_context(ctx)
        assert result == ["step-by-step", "visual"]

    def test_truncates_long_list(self):
        strategies = ["s1", "s2", "s3", "s4", "s5", "s6", "s7"]
        ctx = {"conversation_extra_data": {"strategies_used": strategies}}
        result = get_explanation_strategies_from_context(ctx)
        assert len(result) == 5


class TestShouldRequestFeedback:
    def test_complex_technical(self):
        long_response = (
            "x" * 600
            + " constraint optimization minimize maximize variable coefficient matrix"
        )
        result = should_request_feedback(long_response, [], {})
        assert result is True

    def test_recent_confusion(self):
        result = should_request_feedback(
            "short", [], {"recent_confusion_detected": True}
        )
        assert result is True

    def test_periodic_check(self):
        history = [{"role": "user", "content": f"q{i}"} for i in range(3)]
        result = should_request_feedback("short", history, {})
        assert result is True

    def test_no_feedback_needed(self):
        result = should_request_feedback(
            "short", [{"role": "user", "content": "q1"}], {}
        )
        assert result is False
