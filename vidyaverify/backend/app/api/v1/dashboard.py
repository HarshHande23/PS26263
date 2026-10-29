from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_aicte_or_above
from app.core.enums import UserRole
from app.models.student import Student
from app.models.institution import Institution
from app.models.upload_submission import UploadSubmission
from app.models.validation_finding import ValidationFinding
from app.models.duplicate_case import DuplicateCase
from app.models.alert import Alert
from app.models.user import User
from app.services.analytics_service import compute_data_quality_score, get_analytics_overview

router = APIRouter()


@router.get("/college")
def college_dashboard(
    institution_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Resolve institution
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        inst_id = current_user.institution_id
    else:
        inst_id = institution_id

    student_q = db.query(Student)
    if inst_id:
        student_q = student_q.filter(Student.institution_id == inst_id)

    total_students = student_q.count()
    active_students = student_q.filter(Student.enrolment_status == "active").count()
    verified_students = student_q.filter(Student.verification_status == "verified_by_provider").count()

    finding_q = db.query(ValidationFinding)
    if inst_id:
        finding_q = finding_q.filter(ValidationFinding.institution_id == inst_id)
    open_findings = finding_q.filter(ValidationFinding.status == "open").count()
    error_findings = finding_q.filter(
        ValidationFinding.severity == "error", ValidationFinding.status == "open"
    ).count()

    sub_q = db.query(UploadSubmission)
    if inst_id:
        sub_q = sub_q.filter(UploadSubmission.institution_id == inst_id)
    total_submissions = sub_q.count()

    dup_q = db.query(DuplicateCase)
    if inst_id:
        dup_q = dup_q.filter(
            (DuplicateCase.institution_a_id == inst_id) | (DuplicateCase.institution_b_id == inst_id)
        )
    suspected_duplicates = dup_q.filter(DuplicateCase.status.in_(["suspected", "confirmed"])).count()

    alert_q = db.query(Alert)
    if inst_id:
        alert_q = alert_q.filter(Alert.institution_id == inst_id)
    open_alerts = alert_q.filter(Alert.status == "open").count()

    # Explainable institutional data quality
    data_quality = compute_data_quality_score(inst_id, db)

    return {
        "total_students": total_students,
        "active_students": active_students,
        "verified_students": verified_students,
        "open_findings": open_findings,
        "error_findings": error_findings,
        "total_submissions": total_submissions,
        "suspected_duplicates": suspected_duplicates,
        "open_alerts": open_alerts,
        "data_quality": data_quality,
    }


@router.get("/aicte")
def aicte_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_aicte_or_above),
):
    total_institutions = db.query(Institution).filter_by(is_active=True).count()
    total_students = db.query(Student).count()
    active_students = db.query(Student).filter(Student.enrolment_status == "active").count()
    verified_students = db.query(Student).filter(Student.verification_status == "verified_by_provider").count()
    open_findings = db.query(ValidationFinding).filter(ValidationFinding.status == "open").count()
    suspected_duplicates = db.query(DuplicateCase).filter(DuplicateCase.status.in_(["suspected", "confirmed"])).count()
    open_alerts = db.query(Alert).filter(Alert.status == "open").count()
    total_submissions = db.query(UploadSubmission).count()

    national_dq = compute_data_quality_score(None, db)

    # Per-institution student counts
    inst_counts = (
        db.query(Institution.id, Institution.name, Institution.short_name, Institution.aicte_id, Institution.state)
        .filter_by(is_active=True)
        .all()
    )
    institution_summary = []
    for inst in inst_counts:
        count = db.query(Student).filter(
            Student.institution_id == inst.id,
            Student.enrolment_status == "active",
        ).count()
        institution_summary.append({
            "id": str(inst.id),
            "name": inst.name,
            "short_name": inst.short_name,
            "aicte_id": inst.aicte_id,
            "state": inst.state,
            "active_students": count,
        })

    return {
        "total_institutions": total_institutions,
        "total_students": total_students,
        "active_students": active_students,
        "verified_students": verified_students,
        "open_findings": open_findings,
        "suspected_duplicates": suspected_duplicates,
        "open_alerts": open_alerts,
        "total_submissions": total_submissions,
        "national_data_quality": national_dq,
        "institution_summary": institution_summary,
    }


@router.get("/analytics")
def get_analytics(
    state: Optional[str] = Query(None),
    academic_year_id: Optional[UUID] = Query(None),
    institution_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Detailed analytics dataset for charts and regulatory reporting.
    College administrators are scoped to their institution.
    """
    target_inst = institution_id
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        target_inst = current_user.institution_id

    return get_analytics_overview(
        db=db,
        state_filter=state,
        academic_year_id=academic_year_id,
        institution_id=target_inst,
    )


@router.get("/data-quality")
def get_data_quality(
    institution_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Detailed breakdown of institutional data quality score and actionable suggestions.
    """
    target_inst = institution_id
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        target_inst = current_user.institution_id

    return compute_data_quality_score(target_inst, db)
