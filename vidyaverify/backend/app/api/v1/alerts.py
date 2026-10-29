from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_roles
from app.core.enums import UserRole
from app.models.alert import Alert
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.upload import AlertOut

router = APIRouter()


class AlertTransitionRequest(BaseModel):
    status: str  # "under_review", "awaiting_institution_correction", "resolved", "dismissed"
    resolution_reason: Optional[str] = None


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


@router.post("/{alert_id}/transition", response_model=AlertOut)
def transition_alert(
    alert_id: UUID,
    payload: AlertTransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Formal alert review workflow:
    Transitions alert through OPEN -> UNDER_REVIEW -> AWAITING_INSTITUTION_CORRECTION -> RESOLVED / DISMISSED.
    Requires resolution reason for RESOLVED / DISMISSED.
    College administrators cannot dismiss regulatory AICTE alerts.
    """
    alert = db.query(Alert).filter_by(id=alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    new_status = payload.status.lower()
    valid_statuses = {"open", "under_review", "awaiting_institution_correction", "resolved", "dismissed"}
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid alert status. Permitted: {list(valid_statuses)}",
        )

    # Permission checks: College admins can only review alerts for their own institution
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        if str(alert.institution_id) != str(current_user.institution_id):
            raise HTTPException(status_code=403, detail="Access denied to other institution's alerts")
        # College admins cannot resolve regulatory alerts (e.g. intake exceeded) unilaterally
        if new_status in ("resolved", "dismissed") and alert.alert_type in ("intake_exceeded", "cross_institution_duplicate"):
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Only AICTE Administrators can resolve regulatory intake or duplicate alerts",
            )

    if new_status in ("resolved", "dismissed") and not payload.resolution_reason:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="A resolution reason is required when resolving or dismissing an alert",
        )

    alert.status = new_status
    if payload.resolution_reason:
        alert.message = f"{alert.message or ''} | Note: {payload.resolution_reason}".strip(" |")

    # Audit log entry
    audit = AuditLog(
        user_id=current_user.id,
        action="alert.transition",
        resource_type="Alert",
        resource_id=str(alert.id),
        details={"old_status": alert.status, "new_status": new_status, "reason": payload.resolution_reason},
    )
    db.add(audit)
    db.commit()
    db.refresh(alert)
    return alert
