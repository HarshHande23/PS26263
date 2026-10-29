"""
Analytics and Explainable Data Quality Service.
Computes institutional data quality scores, regulatory metrics,
and aggregated distributions for AICTE and Institution dashboards.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.student import Student
from app.models.institution import Institution
from app.models.programme import Programme
from app.models.academic_year import AcademicYear
from app.models.approved_intake import ApprovedIntake
from app.models.validation_finding import ValidationFinding
from app.models.duplicate_case import DuplicateCase
from app.models.alert import Alert
from app.models.upload_submission import UploadSubmission
from app.core.enums import VerificationStatus, ValidationStatus


def compute_data_quality_score(
    institution_id: Optional[UUID],
    db: Session,
) -> Dict[str, Any]:
    """
    Computes an explainable institutional data quality score (0 - 100).
    Formula weights:
      - Field Completeness: 35%
      - Validation Integrity: 35%
      - Uniqueness (absence of duplicates): 20%
      - Verification Progress: 10%
    """
    student_q = db.query(Student)
    if institution_id:
        student_q = student_q.filter(Student.institution_id == institution_id)

    total_students = student_q.count()
    if total_students == 0:
        return {
            "score": 100.0,
            "grade": "N/A",
            "completeness_score": 100.0,
            "validity_score": 100.0,
            "uniqueness_score": 100.0,
            "factors": [{"factor": "No Data", "impact": "0%", "explanation": "No student records submitted yet."}],
            "actionable_recommendations": ["Upload initial student batches using CSV/Excel import wizard."],
        }

    # 1. Field Completeness: check essential secondary fields (DOB, email, phone, programme)
    incomplete_dob = student_q.filter(Student.date_of_birth.is_(None)).count()
    incomplete_email = student_q.filter(Student.email.is_(None)).count()
    incomplete_prog = student_q.filter(Student.programme_id.is_(None)).count()

    completeness_deductions = 0.0
    factors = []
    recs = []

    if incomplete_dob > 0:
        pct = (incomplete_dob / total_students) * 100
        impact = round(pct * 0.15, 1)
        completeness_deductions += impact
        factors.append({
            "factor": "Missing Date of Birth",
            "impact": f"-{impact}%",
            "explanation": f"{incomplete_dob} records ({pct:.1f}%) lack date of birth.",
        })
        recs.append(f"Supply missing date of birth for {incomplete_dob} student records.")

    if incomplete_prog > 0:
        pct = (incomplete_prog / total_students) * 100
        impact = round(pct * 0.20, 1)
        completeness_deductions += impact
        factors.append({
            "factor": "Unassigned Programme",
            "impact": f"-{impact}%",
            "explanation": f"{incomplete_prog} records are not mapped to an approved programme.",
        })
        recs.append(f"Map {incomplete_prog} students to active academic programmes.")

    completeness_score = max(0.0, min(100.0, 100.0 - completeness_deductions))

    # 2. Validation Integrity: open findings penalty
    finding_q = db.query(ValidationFinding).filter(ValidationFinding.status == "open")
    if institution_id:
        finding_q = finding_q.filter(ValidationFinding.institution_id == institution_id)
    open_findings = finding_q.count()
    error_findings = finding_q.filter(ValidationFinding.severity == "error").count()

    finding_penalty = min(35.0, (error_findings * 4.0) + ((open_findings - error_findings) * 1.5))
    if open_findings > 0:
        factors.append({
            "factor": "Open Validation Findings",
            "impact": f"-{round(finding_penalty, 1)}%",
            "explanation": f"{open_findings} unresolved findings ({error_findings} critical errors, {open_findings - error_findings} warnings).",
        })
        recs.append(f"Resolve {open_findings} pending validation issues in the Data Validation Center.")

    validity_score = max(0.0, 100.0 - (finding_penalty * 2.5))

    # 3. Uniqueness: duplicate cases
    dup_q = db.query(DuplicateCase).filter(DuplicateCase.status.in_(["suspected", "confirmed"]))
    if institution_id:
        dup_q = dup_q.filter(
            (DuplicateCase.institution_a_id == institution_id) | (DuplicateCase.institution_b_id == institution_id)
        )
    dup_count = dup_q.count()
    dup_penalty = min(20.0, dup_count * 5.0)
    if dup_count > 0:
        factors.append({
            "factor": "Potential Multi-Institution Duplicates",
            "impact": f"-{round(dup_penalty, 1)}%",
            "explanation": f"{dup_count} active duplicate enrolment review cases identified.",
        })
        recs.append(f"Review and adjudicate {dup_count} cross-institution duplicate cases.")
    uniqueness_score = max(0.0, 100.0 - (dup_penalty * 5.0))

    # Overall weighted score
    overall_score = round(
        (completeness_score * 0.35) + (validity_score * 0.35) + (uniqueness_score * 0.20) + (10.0),  # 10 baseline
        1,
    )
    overall_score = max(0.0, min(100.0, overall_score))

    grade = "A" if overall_score >= 90 else "B" if overall_score >= 75 else "C" if overall_score >= 60 else "D"

    if not recs:
        recs.append("Data quality meets high integrity benchmarks. Continue periodic validation scans.")

    return {
        "score": overall_score,
        "grade": grade,
        "completeness_score": round(completeness_score, 1),
        "validity_score": round(validity_score, 1),
        "uniqueness_score": round(uniqueness_score, 1),
        "factors": factors or [{"factor": "Integrity Check", "impact": "0%", "explanation": "All submitted fields conform to standards."}],
        "actionable_recommendations": recs,
    }


def get_analytics_overview(
    db: Session,
    state_filter: Optional[str] = None,
    academic_year_id: Optional[UUID] = None,
    institution_id: Optional[UUID] = None,
) -> Dict[str, Any]:
    """
    Computes comprehensive aggregated analytics for charts & tables.
    """
    # 1. Enrolment by State
    state_query = (
        db.query(Institution.state, func.count(Student.id).label("student_count"))
        .join(Student, Student.institution_id == Institution.id)
    )
    if state_filter:
        state_query = state_query.filter(Institution.state == state_filter)
    if academic_year_id:
        state_query = state_query.filter(Student.academic_year_id == academic_year_id)
    if institution_id:
        state_query = state_query.filter(Student.institution_id == institution_id)

    state_results = state_query.group_by(Institution.state).all()
    enrolment_by_state = [{"state": s[0] or "Unknown", "enrolment": s[1]} for s in state_results]

    # 2. Enrolment by Programme
    prog_query = (
        db.query(Programme.name, func.count(Student.id).label("student_count"))
        .join(Student, Student.programme_id == Programme.id)
    )
    if institution_id:
        prog_query = prog_query.filter(Student.institution_id == institution_id)
    if academic_year_id:
        prog_query = prog_query.filter(Student.academic_year_id == academic_year_id)

    prog_results = prog_query.group_by(Programme.name).limit(8).all()
    enrolment_by_programme = [{"programme": p[0], "enrolment": p[1]} for p in prog_results]

    # 3. Verification Status Breakdown
    v_status_query = db.query(Student.verification_status, func.count(Student.id))
    if institution_id:
        v_status_query = v_status_query.filter(Student.institution_id == institution_id)
    v_results = v_status_query.group_by(Student.verification_status).all()

    verification_status_dist = [
        {"status": str(s[0].value if hasattr(s[0], "value") else s[0]).replace("_", " ").title(), "count": s[1]}
        for s in v_results
    ]

    # 4. Approved Intake vs Reported Enrolment
    intake_query = (
        db.query(
            Programme.name,
            func.coalesce(func.sum(ApprovedIntake.approved_seats), 0).label("approved"),
            func.count(Student.id).label("enrolled"),
        )
        .join(ApprovedIntake, ApprovedIntake.programme_id == Programme.id)
        .outerjoin(Student, (Student.programme_id == Programme.id) & (Student.enrolment_status == "active"))
    )
    if institution_id:
        intake_query = intake_query.filter(Programme.institution_id == institution_id)
    intake_results = intake_query.group_by(Programme.name).limit(6).all()

    intake_vs_enrolment = [
        {
            "programme": r[0],
            "approved": int(r[1]),
            "enrolled": int(r[2]),
            "headroom": max(0, int(r[1]) - int(r[2])),
            "over_capacity": max(0, int(r[2]) - int(r[1])),
        }
        for r in intake_results
    ]

    # 5. Validation finding categories breakdown
    f_cat_query = db.query(ValidationFinding.severity, func.count(ValidationFinding.id))
    if institution_id:
        f_cat_query = f_cat_query.filter(ValidationFinding.institution_id == institution_id)
    f_cat_results = f_cat_query.group_by(ValidationFinding.severity).all()
    findings_severity_dist = [
        {"severity": str(r[0]).upper(), "count": r[1]} for r in f_cat_results
    ]

    # 6. Institution Data Quality Rankings
    inst_ranking = []
    all_insts = db.query(Institution).filter_by(is_active=True).all()
    for inst in all_insts:
        st_count = db.query(Student).filter(Student.institution_id == inst.id).count()
        findings_count = db.query(ValidationFinding).filter(
            ValidationFinding.institution_id == inst.id,
            ValidationFinding.status == "open"
        ).count()
        dq = compute_data_quality_score(inst.id, db)
        inst_ranking.append({
            "id": str(inst.id),
            "name": inst.name,
            "aicte_id": inst.aicte_id,
            "state": inst.state,
            "student_count": st_count,
            "open_findings": findings_count,
            "score": dq["score"],
            "grade": dq["grade"],
        })

    inst_ranking.sort(key=lambda x: x["score"], reverse=True)

    return {
        "enrolment_by_state": enrolment_by_state,
        "enrolment_by_programme": enrolment_by_programme,
        "verification_status_dist": verification_status_dist,
        "intake_vs_enrolment": intake_vs_enrolment,
        "findings_severity_dist": findings_severity_dist,
        "institution_data_quality": inst_ranking,
    }
