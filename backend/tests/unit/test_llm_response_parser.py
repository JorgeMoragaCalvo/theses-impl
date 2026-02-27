"""
Unit tests for app.services.llm_response_parser — pure function.
"""
import json

import pytest
from app.services.llm_response_parser import parse_llm_json_response


class TestParseLlmJsonResponse:

    def test_parse_raw_json(self):
        raw = '{"score": 5}'
        result = parse_llm_json_response(raw)
        assert result == {"score": 5}

    def test_parse_json_in_markdown_block(self):
        raw = '```json\n{"score": 5, "feedback": "ok"}\n```'
        result = parse_llm_json_response(raw)
        assert result["score"] == 5
        assert result["feedback"] == "ok"

    def test_parse_generic_codeblock(self):
        raw = '```\n{"key": "value"}\n```'
        result = parse_llm_json_response(raw)
        assert result == {"key": "value"}

    def test_parse_invalid_raises(self):
        with pytest.raises((json.JSONDecodeError, ValueError)):
            parse_llm_json_response("this is not json at all")

    def test_parse_empty_raises(self):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            parse_llm_json_response("   ")

    def test_parse_json_with_surrounding_text(self):
        raw = 'Here is the result: {"answer": 42}'
        # The parser should try to parse the whole stripped text
        # which is not valid JSON, so this should raise
        with pytest.raises((json.JSONDecodeError, ValueError)):
            parse_llm_json_response(raw)
