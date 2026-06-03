"""
Unit tests for app.utils — pure functions, no DB or LLM required.
"""

from app.utils import (
    detect_confusion_signals,
    detect_repeated_topic,
    strip_markdown_images,
)

# ---- strip_markdown_images ----


class TestStripMarkdownImages:
    def test_removes_image_tag(self):
        text = "antes\n![alt](data/course_materials/lp/images/image-01.png)\ndespués"
        result = strip_markdown_images(text)
        assert "![" not in result
        assert "image-01.png" not in result

    def test_preserves_surrounding_text(self):
        text = (
            "## Solución gráfica\n"
            "![sol](data/.../image-02.png)\n"
            "$X = 85, Y = 37.5$\n"
            "*referencia visual*"
        )
        result = strip_markdown_images(text)
        assert "## Solución gráfica" in result
        assert "$X = 85, Y = 37.5$" in result
        assert "*referencia visual*" in result
        assert "![" not in result

    def test_collapses_blank_lines(self):
        text = "linea1\n\n![a](b.png)\n\nlinea2"
        result = strip_markdown_images(text)
        assert "\n\n\n" not in result

    def test_no_images_unchanged(self):
        text = "Maximizar z = 5x + 12y\n- 20x + 10y <= 200"
        assert strip_markdown_images(text) == text

    def test_empty_input(self):
        assert strip_markdown_images("") == ""


# ---- detect_confusion_signals ----


class TestDetectConfusionSignals:
    def test_detect_confusion_high(self):
        result = detect_confusion_signals("no entiendo nada de esto")
        assert result["detected"] is True
        assert result["level"] == "high"

    def test_detect_confusion_medium(self):
        result = detect_confusion_signals("estoy confundido con este tema")
        assert result["detected"] is True
        assert result["level"] == "medium"

    def test_detect_confusion_low(self):
        result = detect_confusion_signals("puedes explicar eso otra vez?")
        assert result["detected"] is True
        assert result["level"] == "low"

    def test_detect_confusion_none(self):
        result = detect_confusion_signals("gracias, entendí perfectamente")
        assert result["detected"] is False
        assert result["level"] == "none"

    def test_detect_confusion_short_response(self):
        result = detect_confusion_signals("??")
        assert result["detected"] is True
        assert "short_confused_response" in result["signals"]

    def test_detect_confusion_multiple_question_marks(self):
        result = detect_confusion_signals("cómo? por qué?")
        assert result["detected"] is True
        assert "multiple_question_marks" in result["signals"]

    def test_detect_confusion_empty_string(self):
        result = detect_confusion_signals("")
        assert result["detected"] is False
        assert result["level"] == "none"


# ---- detect_repeated_topic ----


class TestDetectRepeatedTopic:
    def test_detect_repeated_topic_found(self):
        history = [
            {"role": "user", "content": "explain simplex method please"},
            {"role": "assistant", "content": "The simplex method is..."},
            {"role": "user", "content": "I still don't get the simplex method"},
            {"role": "assistant", "content": "Let me try again..."},
            {"role": "user", "content": "can you explain simplex once more"},
        ]
        result = detect_repeated_topic(history)
        assert result["repeated"] is True
        assert result["count"] >= 2

    def test_detect_repeated_topic_not_enough_messages(self):
        history = [{"role": "user", "content": "hello"}]
        result = detect_repeated_topic(history)
        assert result["repeated"] is False
        assert result["topic"] is None

    def test_detect_repeated_topic_no_repetition(self):
        history = [
            {"role": "user", "content": "explain duality theory"},
            {"role": "assistant", "content": "..."},
            {"role": "user", "content": "now tell me about graphs"},
        ]
        result = detect_repeated_topic(history)
        assert result["repeated"] is False
