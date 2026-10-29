from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_roles
from app.core.enums import UserRole
from app.models.alert import Alert
from app.models.user import User
from app.schemas.upload import AlertOut

router = APIRouter()


@router.get("", response_model=List[AlertOut])
def list_alerts(
    institution_id: Optional[UUID] = None,
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = db.query(Alert)
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        q = q.filter(Alert.institution_id == current_user.institution_id)
    elif institution_id:
        q = q.filter(Alert.institution_id == institution_id)
    if status:
        q = q.filter(Alert.status == status)
    if alert_type:
        q = q.filter(Alert.alert_type == alert_type)
    return q.order_by(Alert.created_at.desc()).limit(limit).all()


@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN
    )),
):
    alert = db.query(Alert).filter_by(id=alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if current_user.role == UserRole.COLLEGE_ADMIN:
        if alert.institution_id != current_user.institution_id:
            raise HTTPException(status_code=403, detail="Access denied")
    alert.status = "acknowledged"
    alert.acknowledged_by_id = current_user.id
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert
