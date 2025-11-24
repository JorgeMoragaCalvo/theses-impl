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

# Alternative Explanations & Adaptive Learning Utilities

def detect_confusion_signals(message: str) -> Dict[str, Any]:
    """
    Detect confusion signals in a student message.

    Args:
        message: Student's message text

    Returns:
        Dictionary with confusion detected (bool), level (none/low/medium/high), and signals (list)
    """
    message_lower = message.lower().strip()

    # Confusion indicators with severity weights
    high_confusion_keywords = [
        "don't understand", "don't get it", "makes no sense", "totally lost",
        "completely confused", "have no idea", "what does this mean",
        "i'm lost", "i am lost", "no clue"
    ]

    medium_confusion_keywords = [
        "confused", "unclear", "not sure", "don't see", "can't figure out",
        "struggling with", "difficulty understanding", "hard to understand",
        "not clear", "doesn't make sense", "how is this"
    ]

    low_confusion_keywords = [
        "what?", "huh?", "wait", "hold on", "can you explain",
        "could you clarify", "what do you mean", "i don't follow",
        "not following", "bit confused"
    ]

    # Very short responses after explanation (potential confusion)
    short_response_patterns = ["?", "??", "???", "what", "huh", "ok?", "why"]

    detected_signals = []
    confusion_level = "none"

    # Check high confusion
    for keyword in high_confusion_keywords:
        if keyword in message_lower:
            detected_signals.append(f"high:{keyword}")
            confusion_level = "high"

    # Check medium confusion
    if confusion_level != "high":
        for keyword in medium_confusion_keywords:
            if keyword in message_lower:
                detected_signals.append(f"medium:{keyword}")
                confusion_level = "medium"

    # Check low confusion
    if confusion_level == "none":
        for keyword in low_confusion_keywords:
            if keyword in message_lower:
                detected_signals.append(f"low:{keyword}")
                confusion_level = "low"

    # Check very short responses
    if len(message_lower) < 15 and any(pattern in message_lower for pattern in short_response_patterns):
        detected_signals.append("short_confused_response")
        if confusion_level == "none":
            confusion_level = "low"

    # Multiple question marks indicate confusion
    if message.count("?") >= 2:
        detected_signals.append("multiple_question_marks")
        if confusion_level == "none":
            confusion_level = "low"

    return {
        "detected": len(detected_signals) > 0,
        "level": confusion_level,
        "signals": detected_signals
    }

def detect_repeated_topic(conversation_history: List[Dict[str, str]], lookback: int = 5) -> Dict[str, Any]:
    """
    Detect if the student is asking about the same topic repeatedly (indicates struggle).

    Args:
        conversation_history: Recent conversation messages
        lookback: Number of recent messages to analyze

    Returns:
        Dictionary with repeated (bool), topic keywords, and count
    """
    if len(conversation_history) < 2:
        return {"repeated": False, "topic": None, "count": 0}

    # Get recent user messages
    recent_user_messages = [
        msg["content"].lower()
        for msg in conversation_history[-lookback:]
        if msg.get("role") == "user"
    ]

    if len(recent_user_messages) < 2:
        return {"repeated": False, "topic": None, "count": 0}

    # Extract key terms (simple approach - look for repeated significant words)
    # In a more sophisticated version, could use NLP techniques
    word_freq = {}
    for message in recent_user_messages:
        words = re.findall(r'\b[a-z]{4,}\b', message)  # Words with 4+ letters
        for word in words:
            # Skip common words
            if word not in ['what', 'how', 'can', 'could', 'would', 'should', 'this', 'that', 'with', 'from']:
                word_freq[word] = word_freq.get(word, 0) + 1

    # Find most repeated terms
    repeated_terms = {word: count for word, count in word_freq.items() if count >= 2}

    if repeated_terms:
        most_repeated = max(repeated_terms.items(), key=lambda x: x[1])
        return {
            "repeated": True,
            "topic": most_repeated[0],
            "count": most_repeated[1],
            "all_repeated_terms": repeated_terms
        }

    return {"repeated": False, "topic": None, "count": 0}

def get_explanation_strategies_from_context(context: Dict[str, Any]) -> List[str]:
    """
    Extract previously used explanation strategies from the conversation context.

    Args:
        context: Conversation context dictionary

    Returns:
        List of strategy names used in recent messages
    """
    strategies = []

    # Check conversation history for strategy metadata
    history = context.get("conversation_history", [])
    for msg in history[-5:]:  # Last 5 messages
        if msg.get("role") == "assistant":
            # In actual implementation, this would come from the message extra_data
            # For now, check if context has strategies_used
            pass

    # Check conversation extra_data for strategies
    conv_extra_data = context.get("conversation_extra_data", {})
    strategies = conv_extra_data.get("strategies_used", [])

    return strategies[-5:] if len(strategies) > 5 else strategies  # Recent 5

def should_request_feedback(response_text: str, conversation_history: List[Dict[str, str]],
                           context: Dict[str, Any]) -> bool:
    """
    Determine if the agent should request understanding feedback from the student.

    Args:
        response_text: The response about to be sent
        conversation_history: Recent conversation
        context: Conversation context

    Returns:
        True if it should request feedback
    """
    # Request feedback if the response is complex (long with technical terms)
    is_complex = len(response_text) > 500

    # Count technical terms (simplified - look for mathematical symbols and key terms)
    technical_indicators = ['∑', '∫', 'equation', 'formula', 'theorem', 'proof',
                           'constraint', 'optimization', 'minimize', 'maximize',
                           'variable', 'coefficient', 'matrix']
    technical_count = sum(1 for indicator in technical_indicators if indicator.lower() in response_text.lower())

    has_technical_content = technical_count >= 3

    # Check if confusion was detected recently
    recent_confusion = context.get("recent_confusion_detected", False)

    # Check message count (request feedback every 3-4 exchanges)
    message_count = len([m for m in conversation_history if m.get("role") == "user"])
    periodic_check = message_count > 0 and message_count % 3 == 0

    # Request feedback if any condition is met
    return (is_complex and has_technical_content) or recent_confusion or periodic_check