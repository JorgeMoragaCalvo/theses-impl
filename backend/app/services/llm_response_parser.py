"""
Utility for parsing LLM responses.
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_llm_json_response(llm_response: str) -> dict[str, Any]:
    """
    Parse the LLM response to extract a JSON object.

    Args:
        llm_response: Raw LLM the response which may contain a JSON object
                      wrapped in Markdown code blocks.

    Returns:
        A dictionary parsed from the JSON object.

    Raises:
        json.JSONDecodeError: If the JSON cannot be decoded.
        ValueError: If the response does not contain a valid JSON object.
    """
    try:
        # Try to extract JSON from the response
        response_text = llm_response.strip()

        # Remove Markdown code blocks if present
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end == -1:
                end = len(response_text)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            if end == -1:
                end = len(response_text)
            response_text = response_text[start:end].strip()

        # If the response_text is empty after stripping Markdown, raise an error
        if not response_text:
            raise ValueError("Stripped response is empty, no JSON found.")

        # Primary parse attempt
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Secondary attempt: extract embedded JSON object from surrounding text
            # (handles cases where the LLM adds preamble/postamble around the JSON)
            json_start = response_text.find("{")
            json_end = response_text.rfind("}")
            if json_start != -1 and json_end > json_start:
                return json.loads(response_text[json_start : json_end + 1])
            raise

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from LLM response: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while parsing LLM response: {e}")
        raise ValueError("Failed to parse LLM response.") from e
