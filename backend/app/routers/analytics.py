from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import Student, get_db
from ..models import ActivityEventBatchCreate
from ..rate_limit import limiter
from ..services.analytics_service import get_analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/events", status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def record_activity_events(
    request: Request,
    batch: ActivityEventBatchCreate,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    """Record a batch of activity events for the current user. Requires authentication."""
    analytics_service = get_analytics_service(db)
    count = analytics_service.record_events(current_user.id, batch.events)
    return {"recorded": count}
