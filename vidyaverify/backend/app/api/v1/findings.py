from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import math
from datetime import datetime, timezone
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_roles
from app.core.enums import UserRole
from app.models.validation_finding import ValidationFinding
from app.models.duplicate_case import DuplicateCase
from app.models.correction_request import CorrectionRequest
from app.models.user import User
from app.schemas.upload import (
    ValidationFindingOut, PaginatedFindings,
    DuplicateCaseOut, CorrectionRequestCreate, CorrectionRequestOut,
    FindingResolveRequest,
)

router = APIRouter()


@router.get("", response_model=PaginatedFindings)
def list_findings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    institution_id: Optional[UUID] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    rule_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = db.query(ValidationFinding)
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        q = q.filter(ValidationFinding.institution_id == current_user.institution_id)
    elif institution_id:
        q = q.filter(ValidationFinding.institution_id == institution_id)
    if severity:
        q = q.filter(ValidationFinding.severity == severity)
    if status:
        q = q.filter(ValidationFinding.status == status)
    if rule_id:
        q = q.filter(ValidationFinding.rule_id == rule_id)

    total = q.count()
    items = q.order_by(ValidationFinding.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return PaginatedFindings(
        items=items, total=total, page=page, size=size,
        pages=math.ceil(total / size) if total else 0,
    )


@router.post("/{finding_id}/resolve", response_model=ValidationFindingOut)
def resolve_finding(
    finding_id: UUID,
    payload: FindingResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN
    )),
):
    finding = db.query(ValidationFinding).filter_by(id=finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    finding.status = "resolved"
    finding.resolved_by_id = current_user.id
    finding.resolved_at = datetime.now(timezone.utc)
    finding.resolution_note = payload.resolution_note
    db.commit()
    db.refresh(finding)
    return finding


@router.post("/{finding_id}/dismiss", response_model=ValidationFindingOut)
def dismiss_finding(
    finding_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN
    )),
):
    finding = db.query(ValidationFinding).filter_by(id=finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    finding.status = "dismissed"
    finding.resolved_by_id = current_user.id
    finding.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(finding)
    return finding


@router.get("/duplicates", response_model=List[DuplicateCaseOut])
def list_duplicates(
    institution_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = db.query(DuplicateCase)
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        inst_id = current_user.institution_id
        q = q.filter(
            (DuplicateCase.institution_a_id == inst_id) | (DuplicateCase.institution_b_id == inst_id)
        )
    elif institution_id:
        q = q.filter(
            (DuplicateCase.institution_a_id == institution_id) |
            (DuplicateCase.institution_b_id == institution_id)
        )
    if status:
        q = q.filter(DuplicateCase.status == status)
    return q.all()


class DuplicateReviewRequest(BaseModel):
    status: str  # "under_review", "confirmed", "dismissed"
    notes: Optional[str] = None


@router.post("/duplicates/{duplicate_id}/review", response_model=DuplicateCaseOut)
def review_duplicate_case(
    duplicate_id: UUID,
    payload: DuplicateReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN)),
):
    case = db.query(DuplicateCase).filter_by(id=duplicate_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Duplicate case not found")
    new_status = payload.status.lower()
    if new_status not in ("under_review", "confirmed", "dismissed"):
        raise HTTPException(status_code=400, detail="Invalid status. Allowed: under_review, confirmed, dismissed")
    case.status = new_status
    case.notes = payload.notes
    case.reviewed_by_id = current_user.id
    case.reviewed_at = datetime.now(timezone.utc)
    
    from app.models.audit_log import AuditLog
    audit = AuditLog(
        user_id=current_user.id,
        action="duplicate_case.reviewed",
        resource_type="DuplicateCase",
        resource_id=str(case.id),
        details={"status": new_status, "notes": payload.notes},
    )
    db.add(audit)
    db.commit()
    db.refresh(case)
    return case


@router.post("/corrections", response_model=CorrectionRequestOut, status_code=201)
def create_correction(
    payload: CorrectionRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF
    )),
):
    cr = CorrectionRequest(
        student_id=payload.student_id,
        finding_id=payload.finding_id,
        requested_by_id=current_user.id,
        field_name=payload.field_name,
        old_value=payload.old_value,
        new_value=payload.new_value,
        justification=payload.justification,
        status="pending",
    )
    db.add(cr)
    db.commit()
    db.refresh(cr)
    return cr


@router.get("/corrections", response_model=List[CorrectionRequestOut])
def list_corrections(
    student_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = db.query(CorrectionRequest)
    if student_id:
        q = q.filter_by(student_id=student_id)
    if status:
        q = q.filter(CorrectionRequest.status == status)
    return q.all()
