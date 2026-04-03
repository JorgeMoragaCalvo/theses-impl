import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import Conversation, Feedback, Message, Student, get_db
from ..models import FeedbackCreate, FeedbackResponse
from ..rate_limit import limiter
from ..utils import sanitize_log_value

logger = logging.getLogger(__name__)

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_feedback(
    request: Request,
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Create feedback for a message. Requires authentication."""
    # Verify message exists
    message = db.query(Message).filter(Message.id == feedback_data.message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Verify the message belongs to a conversation owned by the current user
    conversation = db.query(Conversation).filter(
        Conversation.id == message.conversation_id
    ).first()
    if not conversation or conversation.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to leave feedback on this message"
        )

    # Create feedback (use authenticated user's ID)
    new_feedback = Feedback(
        message_id=feedback_data.message_id,
        student_id=current_user.id,
        rating=feedback_data.rating,
        is_helpful=1 if feedback_data.is_helpful else 0 if feedback_data.is_helpful is not None else None,
        comment=feedback_data.comment
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    safe_feedback = sanitize_log_value(feedback_data.message_id)
    logger.info(f"Created feedback for message {safe_feedback}")

    return FeedbackResponse(
        id=new_feedback.id,
        message_id=new_feedback.message_id,
        student_id=new_feedback.student_id,
        rating=new_feedback.rating,
        is_helpful=bool(new_feedback.is_helpful) if new_feedback.is_helpful is not None else None,
        comment=new_feedback.comment,
        created_at=new_feedback.created_at,
        extra_data=new_feedback.extra_data,
    )
