from typing import List, Dict, Any
import re

"""
Utility functions for the AI Tutoring System.
"""

def format_message_for_llm(role: str, content: str) -> Dict[str, str]:
    """
    Format a message for LLM consumption.

    Args:
        role: Message role ("user", "assistant", "system")
        content: Message content

    Returns:
        Formatted message dictionary
    """
    return {"role": role, "content": content}

def format_conversation_history(messages: List[Any]) -> List[Dict[str, str]]:
    """
    Format database messages for LLM context.

    Args:
        messages: List of Message objects from the database

    Returns:
        List of formatted message dictionaries
    """
    return [
        format_message_for_llm(msg.role, msg.content)
        for msg in messages
    ]

def truncate_text(text: str, max_length: int = 2000, suffix: str = "...") -> str:
    """
    Truncate text to the maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def extract_code_blocks(text: str) -> List[str]:
    """
    Extract code blocks from markdown-formatted text.

    Args:
        text: Text containing Markdown code blocks

    Returns:
        List of code block contents
    """
    patter = r"```(?:\w+)?\n(.*?)```"
    matches = re.findall(patter, text, re.DOTALL)
    return matches

def clean_whitespace(text: str) -> str:
    """
    Clean excessive whitespace from text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    return text.strip()

def count_tokens_estimate(text: str) -> int:
    """
    Estimate token count for text (rough approximation).

    Args:
        text: Text to count

    Returns:
        Estimated token count
    """
    # Estimate: ~4 characters per token
    return len(text) // 4

def format_knowledge_level_context(knowledge_level: str) -> str:
    """
    Format knowledge level for LLM context.

    Args:
        knowledge_level: Knowledge level (beginner, intermediate, advanced)

    Returns:
        Formatted context string
    """
    level_descriptions = {
        "beginner": "This student is new to the topic and needs clear, step-by-step explanations with basic examples.",
        "intermediate": "This student has basic understanding and can handle moderate complexity with some mathematical details.",
        "advanced": "This student is proficient and can engage with theoretical concepts, proofs, and complex problem-solving."
    }
    return level_descriptions.get(knowledge_level.lower(), level_descriptions["beginner"])

def parse_topic_from_message(message: str) -> str:
    """
    Attempt to identify the topic from message content.

    Args:
        message: User message

    Returns:
        Detected topic or "general"
    """
    message_lower = message.lower()

    topic_keywords = {
        "linear_programming": ["linear programming", "lp problem", "simplex", "duality", "constraint",
                               "objective function"],
        "integer_programming": ["integer programming", "ip problem", "binary variable", "branch and bound"],
        "nonlinear_programming": ["nonlinear programming", "nlp", "gradient", "lagrange", "kkt"],
        "operations_research": ["operations research", "or", "optimization"],
        "mathematical_modeling": ["mathematical model", "formulation", "modeling"]
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            return topic
    return "general"

def format_error_message(error: Exception, user_friendly: bool = True) -> str:
    """
    Format error message for display.

    Args:
        error: Exception object
        user_friendly: Whether to show user-friendly message

    Returns:
        Formatted error message
    """
    if user_friendly:
        return (
            "I apologize, but I encountered an issue generating a response. "
            "Please try rephrasing your question or try again in a moment."
        )
    return f"Error: {str(error)}"

def validate_student_knowledge_level(level: str) -> str:
    """
    Validate and normalize knowledge level.

    Args:
        level: Knowledge level string

    Returns:
        Validated level (beginner, intermediate, or advanced)
    """
    valid_levels = ["beginner", "intermediate", "advanced"]
    level_lower = level.lower()

    if level_lower in valid_levels:
        return level_lower

    # Default to beginner if invalid
    return "beginner"