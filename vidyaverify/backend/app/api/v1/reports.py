"""
Regulatory Reporting & Compliance Export Endpoints for VidyaVerify.

Generates official CSV and structured JSON reports:
- Enrolment Summary & Intake Utilization
- Intake Discrepancy & Breach Report
- Validation & Data Quality Findings Report
- System Audit Logs & Chain of Custody Report
- Explainable Statistical Anomalies Report
"""

import io
import csv
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_roles
from app.core.enums import UserRole
from app.models.user import User
from app.models.institution import Institution
from app.models.programme import Programme
from app.models.academic_year import AcademicYear
from app.models.approved_intake import ApprovedIntake
from app.models.student import Student
from app.models.validation_finding import ValidationFinding
from app.models.audit_log import AuditLog
from app.services.anomaly_detector import run_full_anomaly_scan, sync_anomalies_to_alerts

router = APIRouter()


@router.get("/enrolment-summary")
def get_enrolment_summary_report(
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN)),
):
    """
    Institution-wise approved intake capacity vs enrolled students and verification status.
    """
    q = (
        db.query(
            Institution.aicte_id,
            Institution.name.label("institution_name"),
            Institution.state,
            Programme.name.label("programme_name"),
            Programme.code.label("programme_code"),
            AcademicYear.label.label("academic_year_label"),
            ApprovedIntake.approved_seats,
            Programme.institution_id,
            ApprovedIntake.programme_id,
            ApprovedIntake.academic_year_id,
        )
        .join(Programme, ApprovedIntake.programme_id == Programme.id)
        .join(Institution, Programme.institution_id == Institution.id)
        .join(AcademicYear, ApprovedIntake.academic_year_id == AcademicYear.id)
    )

    if current_user.role == UserRole.COLLEGE_ADMIN:
        q = q.filter(Programme.institution_id == current_user.institution_id)

    rows = q.all()
    report_data = []

    for r in rows:
        enrolled_count = (
            db.query(func.count(Student.id))
            .filter(
                Student.programme_id == r.programme_id,
                Student.academic_year_id == r.academic_year_id,
            )
            .scalar()
            or 0
        )
        verified_count = (
            db.query(func.count(Student.id))
            .filter(
                Student.programme_id == r.programme_id,
                Student.academic_year_id == r.academic_year_id,
                Student.verification_status == "VERIFIED_BY_PROVIDER",
            )
            .scalar()
            or 0
        )

        cap = r.approved_seats
        utilization = round((enrolled_count / cap * 100), 1) if cap > 0 else 0.0
        discrepancy = max(0, enrolled_count - cap)

        report_data.append(
            {
                "aicte_id": r.aicte_id,
                "institution_name": r.institution_name,
                "state": r.state or "N/A",
                "programme": f"{r.programme_name} ({r.programme_code})",
                "academic_year": r.academic_year_label,
                "approved_intake": cap,
                "enrolled_students": enrolled_count,
                "verified_students": verified_count,
                "utilization_pct": utilization,
                "capacity_breach_excess": discrepancy,
            }
        )

    if format == "csv":
        output = io.StringIO()
        fieldnames = [
            "aicte_id",
            "institution_name",
            "state",
            "programme",
            "academic_year",
            "approved_intake",
            "enrolled_students",
            "verified_students",
            "utilization_pct",
            "capacity_breach_excess",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_data)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="aicte_enrolment_summary.csv"'},
        )

    return {"count": len(report_data), "data": report_data}


@router.get("/intake-discrepancies")
def get_intake_discrepancies_report(
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN)),
):
    """
    Lists all institutions and programmes where enrolment strictly exceeds approved intake.
    """
    intakes = db.query(ApprovedIntake).all()
    discrepancies = []

    for item in intakes:
        enrolled = (
            db.query(func.count(Student.id))
            .filter(
                Student.programme_id == item.programme_id,
                Student.academic_year_id == item.academic_year_id,
            )
            .scalar()
            or 0
        )
        if enrolled > item.approved_seats:
            excess = enrolled - item.approved_seats
            pct = round((excess / item.approved_seats) * 100, 1) if item.approved_seats > 0 else 100.0
            prog = item.programme
            inst = prog.institution if prog else None
            ay = item.academic_year

            discrepancies.append(
                {
                    "aicte_id": inst.aicte_id if inst else "N/A",
                    "institution_name": inst.name if inst else "N/A",
                    "state": inst.state if inst else "N/A",
                    "programme": prog.name if prog else "N/A",
                    "academic_year": ay.label if ay else "N/A",
                    "approved_intake": item.approved_seats,
                    "actual_enrolment": enrolled,
                    "excess_count": excess,
                    "excess_percentage": pct,
                    "regulatory_action_required": "Initiate Show Cause Notice",
                }
            )

    if format == "csv":
        output = io.StringIO()
        fieldnames = [
            "aicte_id",
            "institution_name",
            "state",
            "programme",
            "academic_year",
            "approved_intake",
            "actual_enrolment",
            "excess_count",
            "excess_percentage",
            "regulatory_action_required",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(discrepancies)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="aicte_intake_discrepancies.csv"'},
        )

    return {"count": len(discrepancies), "data": discrepancies}


@router.get("/validation-findings")
def get_validation_findings_report(
    severity: Optional[str] = None,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN)),
):
    """
    Exports validation and data quality errors found across records.
    """
    q = db.query(ValidationFinding).join(Institution, ValidationFinding.institution_id == Institution.id)

    if current_user.role == UserRole.COLLEGE_ADMIN:
        q = q.filter(ValidationFinding.institution_id == current_user.institution_id)

    if severity:
        q = q.filter(ValidationFinding.severity == severity)

    findings = q.order_by(ValidationFinding.created_at.desc()).limit(1000).all()

    report_data = []
    for f in findings:
        report_data.append(
            {
                "id": str(f.id),
                "institution_id": str(f.institution_id) if f.institution_id else "",
                "submission_id": str(f.submission_id) if f.submission_id else "",
                "student_id": str(f.student_id) if f.student_id else "",
                "rule_id": f.rule_id or "N/A",
                "severity": f.severity.value if hasattr(f.severity, "value") else str(f.severity),
                "title": f.title or "",
                "description": f.description or "",
                "recommendation": f.recommendation or "",
                "status": f.status.value if hasattr(f.status, "value") else str(f.status),
                "created_at": f.created_at.isoformat() if f.created_at else "",
            }
        )

    if format == "csv":
        output = io.StringIO()
        fieldnames = [
            "id",
            "institution_id",
            "submission_id",
            "student_id",
            "rule_id",
            "severity",
            "title",
            "description",
            "recommendation",
            "status",
            "created_at",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_data)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="validation_findings_report.csv"'},
        )

    return {"count": len(report_data), "data": report_data}


@router.get("/anomalies")
def get_anomalies_report(
    sync_alerts: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN)),
):
    """
    Runs explainable anomaly detection scan across institutions and returns findings.
    Optionally syncs findings to persistent regulatory alerts.
    """
    anomalies = run_full_anomaly_scan(db)
    synced_count = 0
    if sync_alerts:
        synced_count = sync_anomalies_to_alerts(db)

    return {
        "count": len(anomalies),
        "synced_to_alerts": synced_count,
        "anomalies": anomalies,
    }


@router.get("/audit-logs")
def get_audit_logs(
    limit: int = Query(50, le=500),
    action: Optional[str] = None,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN)),
):
    """
    Regulatory compliance audit trail.
    """
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))

    logs = q.order_by(AuditLog.created_at.desc()).limit(limit).all()

    data = []
    for log in logs:
        data.append(
            {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else "SYSTEM",
                "action": log.action,
                "resource_type": log.resource_type or "",
                "resource_id": log.resource_id or "",
                "details": str(log.details) if log.details else "",
                "ip_address": log.ip_address or "",
                "created_at": log.created_at.isoformat() if log.created_at else "",
            }
        )

    if format == "csv":
        output = io.StringIO()
        fieldnames = ["id", "user_id", "action", "resource_type", "resource_id", "details", "ip_address", "created_at"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="vidyaverify_audit_trail.csv"'},
        )

    return {"count": len(data), "data": data}
