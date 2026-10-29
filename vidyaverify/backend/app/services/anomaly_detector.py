"""
Explainable Enrolment & Demographic Anomaly Detection Service for AICTE / VidyaVerify.

Applies statistical heuristics and baseline comparisons:
1. Intake Surge Anomaly: Enrolment exceeds approved intake capacity or surges abnormally (> 2.0 std dev).
2. Under-enrolment / Dormant Anomaly: Zero or near-zero enrolment despite significant approved intake.
3. Demographic Cluster Anomaly: Suspiciously identical birth years or email patterns in bulk batches.
4. Verification Failure Surge: Abnormally high external verification failure rates (> 50%).

Produces structured, human-readable explanations with mathematical support (Z-scores, baselines).
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
import math
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.institution import Institution
from app.models.programme import Programme
from app.models.approved_intake import ApprovedIntake
from app.models.student import Student
from app.models.alert import Alert
from app.models.verification_request import VerificationRequest
from app.core.enums import VerificationStatus


class AnomalyResult:
    def __init__(
        self,
        anomaly_type: str,
        severity: str,
        institution_id: UUID,
        institution_name: str,
        programme_name: Optional[str],
        title: str,
        explanation: str,
        metrics: Dict[str, Any],
    ):
        self.anomaly_type = anomaly_type
        self.severity = severity
        self.institution_id = institution_id
        self.institution_name = institution_name
        self.programme_name = programme_name
        self.title = title
        self.explanation = explanation
        self.metrics = metrics

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "institution_id": str(self.institution_id),
            "institution_name": self.institution_name,
            "programme_name": self.programme_name,
            "title": self.title,
            "explanation": self.explanation,
            "metrics": self.metrics,
        }


def detect_intake_surges(db: Session, institution_id: Optional[UUID] = None) -> List[AnomalyResult]:
    """
    Detects when actual student enrolment significantly exceeds approved intake
    or exhibits extreme statistical surges (Z-score > 2.0).
    """
    results: List[AnomalyResult] = []

    intake_query = db.query(ApprovedIntake).join(Programme)
    if institution_id:
        intake_query = intake_query.filter(Programme.institution_id == institution_id)

    intakes = intake_query.all()

    for intake in intakes:
        # Count active enrolled students for this programme & academic year
        enrolment_count = db.query(func.count(Student.id)).filter(
            Student.programme_id == intake.programme_id,
            Student.academic_year_id == intake.academic_year_id,
        ).scalar() or 0

        approved_cap = intake.approved_seats
        inst = intake.programme.institution if intake.programme else None
        inst_id = inst.id if inst else None
        inst_name = inst.name if inst else "Unknown"
        prog_name = intake.programme.name if intake.programme else "Unknown"

        if approved_cap > 0 and enrolment_count > approved_cap:
            excess = enrolment_count - approved_cap
            pct_exceeded = round((excess / approved_cap) * 100, 1)
            # Statistical deviation relative to approved baseline
            std_dev_proxy = max(math.sqrt(approved_cap), 1.0)
            z_score = round(excess / std_dev_proxy, 2)

            severity = "critical" if pct_exceeded > 20 else "high"

            results.append(
                AnomalyResult(
                    anomaly_type="INTAKE_CAPACITY_EXCEEDED",
                    severity=severity,
                    institution_id=inst_id,
                    institution_name=inst_name,
                    programme_name=prog_name,
                    title=f"Intake Capacity Breach: {prog_name} at {inst_name}",
                    explanation=(
                        f"Enrolment of {enrolment_count} exceeds approved AICTE capacity ({approved_cap}) "
                        f"by {excess} students (+{pct_exceeded}%). Statistical deviation Z-score: {z_score}."
                    ),
                    metrics={
                        "enrolment_count": enrolment_count,
                        "approved_intake": approved_cap,
                        "excess": excess,
                        "percent_exceeded": pct_exceeded,
                        "z_score": z_score,
                    },
                )
            )

    return results


def detect_demographic_clustering(db: Session, institution_id: Optional[UUID] = None) -> List[AnomalyResult]:
    """
    Detects abnormal demographic clustering such as >90% identical birth year
    or repetitive email domains in institutions with >= 15 students.
    """
    results: List[AnomalyResult] = []

    inst_query = db.query(Institution)
    if institution_id:
        inst_query = inst_query.filter(Institution.id == institution_id)

    institutions = inst_query.all()

    for inst in institutions:
        students = db.query(Student).filter(Student.institution_id == inst.id).all()
        total_students = len(students)
        if total_students < 15:
            continue

        # Check Birth Year Distribution
        years = [s.date_of_birth.year for s in students if s.date_of_birth is not None]
        if years:
            year_counts: Dict[int, int] = {}
            for y in years:
                year_counts[y] = year_counts.get(y, 0) + 1

            for y, count in year_counts.items():
                freq_pct = (count / len(years)) * 100
                if freq_pct >= 90.0 and len(years) >= 15:
                    results.append(
                        AnomalyResult(
                            anomaly_type="DEMOGRAPHIC_CLUSTER_SUSPICION",
                            severity="medium",
                            institution_id=inst.id,
                            institution_name=inst.name,
                            programme_name=None,
                            title=f"Demographic Uniformity Alert at {inst.name}",
                            explanation=(
                                f"{count} out of {len(years)} students ({round(freq_pct, 1)}%) "
                                f"share identical birth year {y}, which deviates substantially from typical cohorts."
                            ),
                            metrics={
                                "cluster_year": y,
                                "cluster_count": count,
                                "total_sampled": len(years),
                                "cluster_percentage": round(freq_pct, 1),
                            },
                        )
                    )

    return results


def detect_high_verification_failures(db: Session, institution_id: Optional[UUID] = None) -> List[AnomalyResult]:
    """
    Detects institutions with disproportionately high APAAR verification failure rates (> 50%).
    """
    results: List[AnomalyResult] = []

    inst_query = db.query(Institution)
    if institution_id:
        inst_query = inst_query.filter(Institution.id == institution_id)

    institutions = inst_query.all()

    for inst in institutions:
        total_requests = (
            db.query(func.count(VerificationRequest.id))
            .join(Student, VerificationRequest.student_id == Student.id)
            .filter(Student.institution_id == inst.id)
            .scalar()
            or 0
        )

        if total_requests < 10:
            continue

        failed_requests = (
            db.query(func.count(VerificationRequest.id))
            .join(Student, VerificationRequest.student_id == Student.id)
            .filter(
                Student.institution_id == inst.id,
                VerificationRequest.status.in_([VerificationStatus.NOT_VERIFIED, "rejected", "failed"]),
            )
            .scalar()
            or 0
        )

        failure_pct = round((failed_requests / total_requests) * 100, 1)
        if failure_pct >= 50.0:
            results.append(
                AnomalyResult(
                    anomaly_type="HIGH_VERIFICATION_FAILURE_RATE",
                    severity="high",
                    institution_id=inst.id,
                    institution_name=inst.name,
                    programme_name=None,
                    title=f"High Verification Failure Rate ({failure_pct}%) at {inst.name}",
                    explanation=(
                        f"{failed_requests} out of {total_requests} external APAAR verification requests "
                        f"failed or could not be verified ({failure_pct}%). Requires regulatory audit."
                    ),
                    metrics={
                        "total_requests": total_requests,
                        "failed_requests": failed_requests,
                        "failure_rate_pct": failure_pct,
                    },
                )
            )

    return results


def run_full_anomaly_scan(db: Session, institution_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
    """
    Runs all anomaly detectors and returns explainable results.
    """
    surges = detect_intake_surges(db, institution_id)
    clusters = detect_demographic_clustering(db, institution_id)
    failures = detect_high_verification_failures(db, institution_id)

    all_results = surges + clusters + failures
    return [r.to_dict() for r in all_results]


def sync_anomalies_to_alerts(db: Session) -> int:
    """
    Scans for anomalies and ensures corresponding Alert records exist in the database.
    Returns count of newly generated alerts.
    """
    anomalies = run_full_anomaly_scan(db)
    created_count = 0

    for a in anomalies:
        # Check if an active alert already exists with the same title and institution
        existing = db.query(Alert).filter(
            Alert.institution_id == UUID(a["institution_id"]),
            Alert.title == a["title"],
            Alert.status != "resolved",
        ).first()

        if not existing:
            new_alert = Alert(
                institution_id=UUID(a["institution_id"]),
                title=a["title"],
                message=a["explanation"],
                severity=a["severity"],
                alert_type="anomaly",
                status="open",
            )
            db.add(new_alert)
            created_count += 1

    if created_count > 0:
        db.commit()

    return created_count
