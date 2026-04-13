import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..agents.integer_programming_agent import get_integer_programming_agent
from ..agents.linear_programming_agent import get_linear_programming_agent
from ..agents.mathematical_modeling_agent import get_mathematical_modeling_agent
from ..agents.nlp_agent import get_nonlinear_programming_agent
from ..agents.operations_research_agent import get_operations_research_agent
from ..auth import get_current_user
from ..database import Conversation, Message, Student, get_db
from ..enums import UserRole
from ..models import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse,
)
from ..rate_limit import limiter
from ..services.affect_service import get_affect_service
from ..services.conversation_service import get_conversation_service
from ..services.spaced_repetition_service import get_spaced_repetition_service
from ..tools.spaced_repetition_tool import SpacedRepetitionReviewTool
from ..utils import detect_confusion_signals, sanitize_log_value

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# Agent Registry - Maps topic names to agent getter functions
AGENT_REGISTRY = {
    "operations_research": get_operations_research_agent,
    "linear_programming": get_linear_programming_agent,
    "mathematical_modeling": get_mathematical_modeling_agent,
    "nonlinear_programming": get_nonlinear_programming_agent,
    "integer_programming": get_integer_programming_agent,
}


def get_agent_for_topic(topic: str):
    """
    Get the appropriate agent for a given topic.

    Args:
        topic: Topic string (e.g., "linear_programming", "mathematical_modeling")

    Returns:
        Agent instance for the specified topic
    """
    agent_getter = AGENT_REGISTRY.get(topic)
    safe_topic = sanitize_log_value(topic)
    if agent_getter is None:
        logger.warning(
            f"No agent found for topic '{safe_topic}', falling back to linear programming agent"
        )
        return get_linear_programming_agent()

    logger.info(f"Selected agent for topic: {safe_topic}")
    return agent_getter()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """
    Send a message and get the AI tutor response.
    Requires authentication.
    """
    # Use authenticated user's ID instead of request data
    student_id = current_user.id

    # Get or create conversation
    conversation = None
    if chat_request.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == chat_request.conversation_id,
                Conversation.is_active == 1,
            )
            .first()
        )

    if not conversation:
        # Create the new conversation
        conversation = Conversation(
            student_id=student_id, topic=chat_request.topic, is_active=1
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Verify the conversation belongs to the authenticated user
    if conversation.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    # Save user message
    user_message = Message(
        conversation_id=conversation.id, role="user", content=chat_request.message
    )
    db.add(user_message)
    db.commit()

    affect_extra: dict = {}
    try:
        # Get the appropriate agent based on the topic
        topic_value = chat_request.topic.value  # Get string value from enum
        agent = get_agent_for_topic(topic_value)

        # Get conversation service
        conversation_service = get_conversation_service(db)

        # Retrieve conversation history (last 10 messages)
        conversation_history = conversation_service.get_conversation_history(
            conversation_id=conversation.id
        )

        # Get student context with the actual topic
        context = conversation_service.get_conversation_context(
            conversation_id=conversation.id, student_id=student_id, topic=topic_value
        )

        # Fetch due spaced-repetition reviews and attach to context
        srs = get_spaced_repetition_service(db)
        context["due_reviews"] = srs.get_due_reviews(student_id, topic=topic_value)

        # Provide a spaced repetition tool so the agent can record review results
        if context["due_reviews"]:
            context["tools"] = [
                SpacedRepetitionReviewTool(db=db, student_id=student_id)
            ]

        # Detect student affective state from session activity events
        if chat_request.session_id:
            confusion_for_affect = detect_confusion_signals(chat_request.message)
            affect_svc = get_affect_service(db)
            affect_result = affect_svc.detect(
                student_id=student_id,
                session_id=chat_request.session_id,
                confusion_analysis=confusion_for_affect,
            )
            context["affect_analysis"] = affect_result
            affect_extra = {
                "affect_state": affect_result.get("state", "neutral"),
                "affect_signals": affect_result.get("signals", []),
            }

        # Generate AI response using the selected agent
        response_text = agent.generate_response(
            user_message=chat_request.message,
            conversation_history=conversation_history,
            context=context,
        )
        agent_type = agent.agent_type

        logger.info(
            f"Generated response for student {student_id} using {agent_type} agent: {len(response_text)} chars"
        )
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        response_text = (
            "I apologize, but I encountered an error processing your request. "
            "Please try again or rephrase your question."
        )
        agent_type = "error"

    # Save the assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        agent_type=agent_type,
        extra_data=affect_extra,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        response=response_text,
        agent_type=agent_type,
        topic=chat_request.topic,
        timestamp=assistant_message.timestamp,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """Get conversation by ID with all messages. Requires authentication."""
    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    # Users can only view their own conversations
    if (
        conversation.student_id != current_user.id
        and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this conversation",
        )

    # Get all messages in conversation
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp)
        .all()
    )

    conv = ConversationResponse.model_validate(conversation)
    conv.messages = [MessageResponse.model_validate(msg) for msg in messages]
    return conv


@router.get(
    "/students/{student_id}/conversations", response_model=list[ConversationResponse]
)
async def get_student_conversations(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """Get all conversations for a student. Requires authentication."""
    # Users can only view their own conversations, admins can view any
    if current_user.id != student_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these conversations",
        )

    conversations = (
        db.query(Conversation)
        .filter(Conversation.student_id == student_id)
        .order_by(Conversation.started_at.desc())
        .all()
    )

    return [ConversationResponse.model_validate(conv) for conv in conversations]
