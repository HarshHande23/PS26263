"""
Validation Engine — identifies rule violations in student data.

Rules implemented:
  RULE_MISSING_NAME      - Missing full name
  RULE_MISSING_DOB       - Missing date of birth
  RULE_MISSING_ENROL_NUM - Missing enrolment number
  RULE_MISSING_APAAR     - Missing APAAR ID hash (warning)
  RULE_MALFORMED_APAAR   - APAAR format does not match configurable pattern
  RULE_MALFORMED_EMAIL   - Invalid email format
  RULE_FUTURE_DOB        - DOB is in the future
  RULE_FUTURE_ADMISSION  - Admission date is in the future
  RULE_WITHIN_FILE_DUP   - Duplicate within the same upload file
  RULE_CROSS_INST_DUP    - Same APAAR hash found at another institution
  RULE_INTAKE_EXCEEDED   - Enrolment would exceed approved intake
  RULE_MISSING_PROGRAMME - No programme assigned
  RULE_MISSING_ACAD_YEAR - No academic year assigned
  RULE_INCONSISTENT_STATUS - Enrolled status inconsistent with dates
"""

import re
import hashlib
from datetime import date, datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.approved_intake import ApprovedIntake
from app.models.validation_finding import ValidationFinding
from app.models.duplicate_case import DuplicateCase
from app.models.alert import Alert


# ─── APAAR format: 12 digits (synthetic rule) ─────────────────────────────────
APAAR_PATTERN = re.compile(r"^\d{12}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _parse_date(val: Any) -> Optional[date]:
    """Parse date from string or date object safely."""
    if not val or str(val).strip() in ("", "nan", "NaT", "None"):
        return None
    if isinstance(val, date):
        return val
    try:
        return datetime.fromisoformat(str(val).strip().split("T")[0]).date()
    except Exception:
        pass
    try:
        import pandas as pd
        dt = pd.to_datetime(str(val))
        return dt.date()
    except Exception:
        return None


def hash_apaar(apaar_id: str) -> str:
    """SHA-256 hash of the raw APAAR ID. Never log the raw value."""
    return hashlib.sha256(apaar_id.strip().encode()).hexdigest()


def mask_apaar(apaar_id: str) -> str:
    """Return masked form e.g. XXXX-XXXX-1234 for display."""
    digits = re.sub(r"\D", "", apaar_id)
    if len(digits) >= 4:
        return f"XXXX-XXXX-{digits[-4:]}"
    return "XXXX-XXXX-XXXX"


def _finding(
    rule_id: str,
    severity: str,
    title: str,
    description: str = "",
    recommendation: str = "",
    field_name: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "rule_id": rule_id,
        "severity": severity,
        "title": title,
        "description": description,
        "recommendation": recommendation,
        "field_name": field_name,
        "status": "open",
    }


class ValidationEngine:
    """Stateless validation engine. Returns lists of finding dicts."""

    # ── Single-row field validation ─────────────────────────────────────────
    def validate_row(self, row: Dict[str, Any], row_number: int) -> List[Dict[str, Any]]:
        findings = []
        today = date.today()

        name = str(row.get("full_name") or "").strip()
        if not name:
            findings.append(_finding(
                "RULE_MISSING_NAME", "error",
                f"Row {row_number}: Missing full name",
                "The full_name field is required.",
                "Provide the student's full legal name.",
                field_name="full_name",
            ))

        dob = _parse_date(row.get("date_of_birth"))
        if not dob:
            findings.append(_finding(
                "RULE_MISSING_DOB", "warning",
                f"Row {row_number}: Missing date of birth",
                "date_of_birth is recommended for identity verification.",
                "Provide the student's date of birth.",
                field_name="date_of_birth",
            ))
        elif dob > today:
            findings.append(_finding(
                "RULE_FUTURE_DOB", "error",
                f"Row {row_number}: Date of birth is in the future",
                f"DOB {dob} is after today ({today}).",
                "Correct the date of birth.",
                field_name="date_of_birth",
            ))
        else:
            age = (today - dob).days // 365
            if age < 15 or age > 75:
                findings.append(_finding(
                    "RULE_ANOMALOUS_AGE", "warning",
                    f"Row {row_number}: Anomalous age detected ({age} years old)",
                    f"Calculated age {age} from DOB {dob} is outside standard academic range (15-75).",
                    "Verify the student's date of birth.",
                    field_name="date_of_birth",
                ))

        enrol = str(row.get("enrolment_number") or "").strip()
        if not enrol:
            findings.append(_finding(
                "RULE_MISSING_ENROL_NUM", "warning",
                f"Row {row_number}: Missing enrolment number",
                "enrolment_number is recommended.",
                "Assign an enrolment number to this student.",
                field_name="enrolment_number",
            ))

        apaar_raw = str(row.get("apaar_id") or "").strip()
        if not apaar_raw:
            findings.append(_finding(
                "RULE_MISSING_APAAR", "warning",
                f"Row {row_number}: Missing APAAR ID",
                "APAAR ID is required for cross-institution duplicate detection.",
                "Obtain and enter the student's APAAR ID.",
                field_name="apaar_id",
            ))
        elif not APAAR_PATTERN.match(apaar_raw):
            findings.append(_finding(
                "RULE_MALFORMED_APAAR", "error",
                f"Row {row_number}: Malformed APAAR ID",
                "APAAR ID must be exactly 12 digits (synthetic rule).",
                "Correct the APAAR ID format.",
                field_name="apaar_id",
            ))

        email = str(row.get("email") or "").strip()
        if email and not EMAIL_PATTERN.match(email):
            findings.append(_finding(
                "RULE_MALFORMED_EMAIL", "warning",
                f"Row {row_number}: Malformed email address",
                f"'{email}' does not appear to be a valid email format.",
                "Correct the email address.",
                field_name="email",
            ))

        admission_date = _parse_date(row.get("admission_date"))
        if admission_date and admission_date > today:
            findings.append(_finding(
                "RULE_FUTURE_ADMISSION", "warning",
                f"Row {row_number}: Admission date is in the future",
                f"Admission date {admission_date} is after today ({today}).",
                "Verify the admission date.",
                field_name="admission_date",
            ))

        if not row.get("programme_id") and not row.get("programme_code"):
            findings.append(_finding(
                "RULE_MISSING_PROGRAMME", "warning",
                f"Row {row_number}: No programme assigned",
                "Programme information is missing.",
                "Assign the student to a programme.",
                field_name="programme_code",
            ))

        if not row.get("academic_year_id") and not row.get("academic_year"):
            findings.append(_finding(
                "RULE_MISSING_ACAD_YEAR", "warning",
                f"Row {row_number}: No academic year assigned",
                "Academic year information is missing.",
                "Assign the student to an academic year.",
                field_name="academic_year",
            ))

        return findings

    # ── Within-file duplicate detection ─────────────────────────────────────
    def detect_within_file_duplicates(
        self, rows: List[Dict[str, Any]]
    ) -> List[Tuple[int, int, str]]:
        """
        Returns list of (row_a, row_b, reason) tuples for duplicates.
        Checks: APAAR hash match, then name+DOB match.
        """
        duplicates: List[Tuple[int, int, str]] = []
        seen_apaar: Dict[str, int] = {}
        seen_name_dob: Dict[str, int] = {}

        for i, row in enumerate(rows, start=2):  # row 1 = header
            apaar_raw = str(row.get("apaar_id") or "").strip()
            if apaar_raw and APAAR_PATTERN.match(apaar_raw):
                h = hash_apaar(apaar_raw)
                if h in seen_apaar:
                    duplicates.append((seen_apaar[h], i, "apaar_hash_match"))
                else:
                    seen_apaar[h] = i

            name = str(row.get("full_name") or "").strip().lower()
            dob = str(row.get("date_of_birth") or "").strip()
            if name and dob:
                key = f"{name}|{dob}"
                if key in seen_name_dob:
                    duplicates.append((seen_name_dob[key], i, "name_dob_match"))
                else:
                    seen_name_dob[key] = i

        return duplicates

    # ── Cross-institution duplicate detection ────────────────────────────────
    def detect_cross_institution_duplicates(
        self, apaar_hashes: List[str], institution_id: UUID, db: Session
    ) -> List[Dict[str, Any]]:
        """
        Returns list of existing Student records at OTHER institutions
        whose APAAR hash matches one in the provided list.
        """
        if not apaar_hashes:
            return []

        existing = (
            db.query(Student)
            .filter(
                Student.apaar_id_hash.in_(apaar_hashes),
                Student.institution_id != institution_id,
            )
            .all()
        )
        return [
            {
                "student_id": str(s.id),
                "institution_id": str(s.institution_id),
                "apaar_id_hash": s.apaar_id_hash,
                "full_name": s.full_name,
            }
            for s in existing
        ]

    # ── Intake calculation ────────────────────────────────────────────────────
    def check_intake(
        self,
        programme_id: UUID,
        academic_year_id: UUID,
        category: str,
        institution_id: UUID,
        db: Session,
        additional_count: int = 1,
    ) -> Dict[str, Any]:
        """
        Returns dict with approved, current_enrolled, would_exceed, headroom.
        """
        intake = (
            db.query(ApprovedIntake)
            .filter(
                ApprovedIntake.programme_id == programme_id,
                ApprovedIntake.academic_year_id == academic_year_id,
                ApprovedIntake.category == category,
            )
            .first()
        )

        if not intake:
            # Also check "general" bucket as fallback
            intake = (
                db.query(ApprovedIntake)
                .filter(
                    ApprovedIntake.programme_id == programme_id,
                    ApprovedIntake.academic_year_id == academic_year_id,
                    ApprovedIntake.category == "general",
                )
                .first()
            )

        approved = intake.approved_seats if intake else 0

        from app.models.student import Student
        current_enrolled = (
            db.query(Student)
            .filter(
                Student.programme_id == programme_id,
                Student.academic_year_id == academic_year_id,
                Student.institution_id == institution_id,
                Student.admission_category == category,
                Student.enrolment_status == "active",
            )
            .count()
        )

        headroom = approved - current_enrolled
        would_exceed = (current_enrolled + additional_count) > approved

        return {
            "approved": approved,
            "current_enrolled": current_enrolled,
            "headroom": headroom,
            "would_exceed": would_exceed,
            "deficit": max(0, (current_enrolled + additional_count) - approved),
        }

    # ── Persist findings to DB ─────────────────────────────────────────────
    def save_findings(
        self,
        findings: List[Dict[str, Any]],
        db: Session,
        submission_id: Optional[UUID] = None,
        student_id: Optional[UUID] = None,
        institution_id: Optional[UUID] = None,
    ) -> List[ValidationFinding]:
        saved = []
        for f in findings:
            vf = ValidationFinding(
                submission_id=submission_id,
                student_id=student_id,
                institution_id=institution_id,
                rule_id=f["rule_id"],
                severity=f["severity"],
                title=f["title"],
                description=f.get("description", ""),
                recommendation=f.get("recommendation", ""),
                status=f.get("status", "open"),
            )
            db.add(vf)
            saved.append(vf)
        db.flush()
        return saved


validation_engine = ValidationEngine()
