"""
Import Service — handles CSV/XLSX parsing, row validation, deduplication,
intake checking, DB insertion, and result summarization.
"""

import io
import hashlib
from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.upload_submission import UploadSubmission
from app.models.import_error import ImportError as ImportErrorModel
from app.models.duplicate_case import DuplicateCase
from app.models.alert import Alert
from app.models.programme import Programme
from app.models.academic_year import AcademicYear
from app.services.validation_engine import validation_engine, hash_apaar, mask_apaar, APAAR_PATTERN
from app.core.enums import SubmissionStatus

# Required columns in the import template
REQUIRED_COLUMNS = {"full_name"}
OPTIONAL_COLUMNS = {
    "apaar_id", "date_of_birth", "gender", "email", "phone",
    "enrolment_number", "programme_code", "academic_year",
    "admission_date", "admission_category",
    "is_supernumerary", "is_nri", "is_oci", "is_foreign_national", "is_pwd",
}
ALL_EXPECTED_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS


def parse_file(file_bytes: bytes, filename: str) -> Tuple[pd.DataFrame, str]:
    """Parse CSV or XLSX and return (DataFrame, detected_type)."""
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        df = pd.read_csv(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
        return df, "csv"
    elif ext in ("xlsx", "xls"):
        df = pd.read_excel(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
        return df, "xlsx"
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def _coerce_date(val: Any) -> Optional[date]:
    if not val or str(val).strip() in ("", "nan", "NaT"):
        return None
    try:
        return pd.to_datetime(str(val)).date()
    except Exception:
        return None


def _coerce_bool(val: Any) -> bool:
    return str(val).strip().lower() in ("1", "true", "yes", "y")


def clean_row_data(row: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and safely mask row data for persistence and export."""
    cleaned = {}
    for k, v in row.items():
        if k == "apaar_id":
            cleaned["apaar_id"] = mask_apaar(str(v or ""))
        else:
            cleaned[k] = "" if (v is None or str(v).lower() == "nan") else str(v)
    return cleaned


def process_submission(
    submission: UploadSubmission,
    file_bytes: bytes,
    institution_id: UUID,
    db: Session,
) -> UploadSubmission:
    """
    Full import pipeline. Mutates submission with results and commits.
    Returns updated submission.
    """
    submission.status = SubmissionStatus.PROCESSING.value
    db.flush()

    try:
        df, file_type = parse_file(file_bytes, submission.filename)
    except ValueError as e:
        submission.status = SubmissionStatus.FAILED.value
        submission.error_summary = str(e)
        submission.completed_at = datetime.now(timezone.utc)
        db.flush()
        return submission

    submission.file_type = file_type
    submission.total_rows = len(df)

    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Check required columns
    missing_req = REQUIRED_COLUMNS - set(df.columns)
    if missing_req:
        submission.status = SubmissionStatus.FAILED.value
        submission.error_summary = f"Missing required columns: {missing_req}"
        submission.completed_at = datetime.now(timezone.utc)
        db.flush()
        return submission

    rows = df.to_dict(orient="records")

    # ── Phase 1: single-row field validation ──────────────────────────────
    row_findings: Dict[int, List[Dict]] = {}
    for i, row in enumerate(rows, start=2):
        findings = validation_engine.validate_row(row, i)
        if findings:
            row_findings[i] = findings

    # ── Phase 2: within-file duplicate detection ──────────────────────────
    within_dups: List[Tuple[int, int, str]] = validation_engine.detect_within_file_duplicates(rows)
    dup_row_indices = set()
    second_occurrence_dups = set()
    dup_details: Dict[int, Dict[str, Any]] = {}

    for a, b, reason in within_dups:
        dup_row_indices.add(a)
        dup_row_indices.add(b)
        second_occurrence_dups.add(b)
        dup_details[b] = {
            "partner": a,
            "rule": "RULE_DUPLICATE_ROW",
            "message": f"Row {b}: Duplicate record rejected — identical APAAR ID matches earlier Row {a}.",
        }
        if a not in dup_details:
            dup_details[a] = {
                "partner": b,
                "rule": "RULE_DUPLICATE_COLLISION",
                "message": f"Row {a}: Within-file duplicate collision — matches identical APAAR ID in Row {b}.",
            }

    # ── Phase 3: cross-institution duplicate detection ────────────────────
    apaar_hashes_in_file = []
    hash_to_row_index: Dict[str, int] = {}
    for i, row in enumerate(rows, start=2):
        apaar_raw = str(row.get("apaar_id") or "").strip()
        if apaar_raw and APAAR_PATTERN.match(apaar_raw):
            h = hash_apaar(apaar_raw)
            apaar_hashes_in_file.append(h)
            hash_to_row_index[h] = i

    cross_dups = validation_engine.detect_cross_institution_duplicates(
        apaar_hashes_in_file, institution_id, db
    )
    cross_dup_hashes = {d["apaar_id_hash"] for d in cross_dups}

    # ── Phase 4: Look up programmes and academic years by code/label ───────
    programmes = {p.code: p for p in db.query(Programme).filter_by(institution_id=institution_id).all()}
    academic_years = {ay.label: ay for ay in db.query(AcademicYear).filter_by(institution_id=institution_id).all()}

    # ── Phase 5: Import valid rows ─────────────────────────────────────────
    valid_count = 0
    invalid_count = 0
    dup_count = 0
    imported_count = 0
    skipped_count = 0
    intake_exceeded_count = 0

    for i, row in enumerate(rows, start=2):
        fatal_errors = [f for f in row_findings.get(i, []) if f.get("severity") == "error"]
        warning_findings = [f for f in row_findings.get(i, []) if f.get("severity") != "error"]
        has_fatal = bool(fatal_errors)
        is_second_dup = i in second_occurrence_dups
        is_first_dup = i in dup_details and not is_second_dup
        apaar_raw = str(row.get("apaar_id") or "").strip()
        apaar_hash = hash_apaar(apaar_raw) if (apaar_raw and APAAR_PATTERN.match(apaar_raw)) else None
        is_cross_dup = apaar_hash in cross_dup_hashes if apaar_hash else False

        row_dict_clean = clean_row_data(row)

        if has_fatal:
            invalid_count += 1
            skipped_count += 1
            # Persist fatal import errors
            for f in fatal_errors:
                err = ImportErrorModel(
                    submission_id=submission.id,
                    row_number=i,
                    row_data=row_dict_clean,
                    error_type=f["rule_id"],
                    field_name=f.get("field_name"),
                    error_message=f["title"],
                )
                db.add(err)
            # Also record any non-fatal warnings for this row
            for f in warning_findings:
                err = ImportErrorModel(
                    submission_id=submission.id,
                    row_number=i,
                    row_data=row_dict_clean,
                    error_type=f["rule_id"],
                    field_name=f.get("field_name"),
                    error_message=f["title"],
                )
                db.add(err)
            continue

        if is_second_dup:
            dup_count += 1
            invalid_count += 1
            skipped_count += 1
            err = ImportErrorModel(
                submission_id=submission.id,
                row_number=i,
                row_data=row_dict_clean,
                error_type="RULE_DUPLICATE_ROW",
                field_name="apaar_id",
                error_message=dup_details[i]["message"],
            )
            db.add(err)
            continue

        if is_first_dup:
            dup_count += 1
            err = ImportErrorModel(
                submission_id=submission.id,
                row_number=i,
                row_data=row_dict_clean,
                error_type="RULE_DUPLICATE_COLLISION",
                field_name="apaar_id",
                error_message=dup_details[i]["message"],
            )
            db.add(err)

        if is_cross_dup:
            dup_count += 1
            err = ImportErrorModel(
                submission_id=submission.id,
                row_number=i,
                row_data=row_dict_clean,
                error_type="RULE_CROSS_INST_DUP",
                field_name="apaar_id",
                error_message=f"Row {i}: Cross-institution duplicate — student APAAR already exists at another AICTE institution.",
            )
            db.add(err)

        # Record warnings / anomalies (e.g. malformed email, anomalous age, future admission)
        for f in warning_findings:
            err = ImportErrorModel(
                submission_id=submission.id,
                row_number=i,
                row_data=row_dict_clean,
                error_type=f["rule_id"],
                field_name=f.get("field_name"),
                error_message=f["title"],
            )
            db.add(err)

        # Resolve programme/academic year
        prog_code = str(row.get("programme_code") or "").strip()
        prog = programmes.get(prog_code)
        ay_label = str(row.get("academic_year") or "").strip()
        ay = academic_years.get(ay_label)

        # Intake check
        intake_exceeded = False
        if prog and ay:
            cat = str(row.get("admission_category") or "general").strip().lower()
            intake_info = validation_engine.check_intake(
                prog.id, ay.id, cat, institution_id, db
            )
            if intake_info["would_exceed"]:
                intake_exceeded = True
                intake_exceeded_count += 1
                alert = Alert(
                    institution_id=institution_id,
                    alert_type="intake_exceeded",
                    severity="error",
                    title=f"Intake exceeded for {prog.name} ({cat})",
                    message=(
                        f"Row {i}: Approved={intake_info['approved']}, "
                        f"Enrolled={intake_info['current_enrolled']}. "
                        f"This admission would exceed the limit."
                    ),
                    related_submission_id=submission.id,
                    status="open",
                )
                db.add(alert)
                err = ImportErrorModel(
                    submission_id=submission.id,
                    row_number=i,
                    row_data=row_dict_clean,
                    error_type="RULE_INTAKE_EXCEEDED",
                    field_name="programme_code",
                    error_message=f"Row {i}: Admission would exceed approved intake limit for {prog.name}.",
                )
                db.add(err)

        # Check for re-import (same enrolment_number at same institution)
        enrol_num = str(row.get("enrolment_number") or "").strip() or None
        if enrol_num:
            existing = db.query(Student).filter_by(
                institution_id=institution_id,
                enrolment_number=enrol_num,
            ).first()
            if existing:
                err = ImportErrorModel(
                    submission_id=submission.id,
                    row_number=i,
                    row_data=row_dict_clean,
                    error_type="RULE_REIMPORT",
                    field_name="enrolment_number",
                    error_message=f"Student with enrolment number '{enrol_num}' already exists.",
                )
                db.add(err)
                skipped_count += 1
                invalid_count += 1
                continue

        # Create student record
        student = Student(
            institution_id=institution_id,
            full_name=str(row.get("full_name") or "").strip(),
            date_of_birth=_coerce_date(row.get("date_of_birth")),
            gender=str(row.get("gender") or "").strip() or None,
            email=str(row.get("email") or "").strip() or None,
            phone=str(row.get("phone") or "").strip() or None,
            enrolment_number=enrol_num,
            apaar_id_hash=apaar_hash,
            apaar_id_masked=mask_apaar(apaar_raw) if apaar_raw else None,
            programme_id=prog.id if prog else None,
            academic_year_id=ay.id if ay else None,
            admission_date=_coerce_date(row.get("admission_date")),
            admission_category=str(row.get("admission_category") or "general").strip().lower(),
            is_supernumerary=_coerce_bool(row.get("is_supernumerary")),
            is_nri=_coerce_bool(row.get("is_nri")),
            is_oci=_coerce_bool(row.get("is_oci")),
            is_foreign_national=_coerce_bool(row.get("is_foreign_national")),
            is_pwd=_coerce_bool(row.get("is_pwd")),
        )
        db.add(student)
        db.flush()

        # Save findings for this student
        all_row_findings = list(row_findings.get(i, []))
        if is_cross_dup:
            for cd in cross_dups:
                if apaar_hash == cd["apaar_id_hash"]:
                    dup_finding = {
                        "rule_id": "RULE_CROSS_INST_DUP",
                        "severity": "warning",
                        "title": f"Potential duplicate at another institution",
                        "description": (
                            f"Student '{student.full_name}' has the same APAAR hash as "
                            f"a record at institution {cd['institution_id']}."
                        ),
                        "recommendation": "Review both records before confirming enrolment.",
                        "status": "open",
                    }
                    all_row_findings.append(dup_finding)

                    # Create DuplicateCase record
                    dup_case = DuplicateCase(
                        student_a_id=student.id,
                        student_b_id=cd["student_id"],
                        institution_a_id=institution_id,
                        institution_b_id=cd["institution_id"],
                        match_reason="apaar_hash_match",
                        confidence="high",
                        status="suspected",
                    )
                    db.add(dup_case)

        if all_row_findings:
            validation_engine.save_findings(
                all_row_findings, db,
                submission_id=submission.id,
                student_id=student.id,
                institution_id=institution_id,
            )

        valid_count += 1
        imported_count += 1

    # ── Finalize submission ────────────────────────────────────────────────
    submission.valid_rows = valid_count
    submission.invalid_rows = invalid_count
    submission.duplicate_rows = dup_count
    submission.imported_rows = imported_count
    submission.skipped_rows = skipped_count
    submission.intake_exceeded_rows = intake_exceeded_count
    submission.status = SubmissionStatus.COMPLETED.value
    submission.completed_at = datetime.now(timezone.utc)
    db.flush()

    return submission


def generate_rejected_csv(submission_id: UUID, db: Session) -> bytes:
    """Return a CSV of all rejected rows, duplicates, and anomalies for a submission."""
    errors = (
        db.query(ImportErrorModel)
        .filter_by(submission_id=submission_id)
        .order_by(ImportErrorModel.row_number.asc())
        .all()
    )
    records = []
    for e in errors:
        rec = {
            "row_number": e.row_number,
            "error_type": e.error_type,
            "field_name": e.field_name or "",
            "error_message": e.error_message,
        }
        if e.row_data and isinstance(e.row_data, dict):
            for k, v in e.row_data.items():
                if k not in rec:
                    rec[k] = v
        records.append(rec)

    if not records:
        return b"row_number,error_type,field_name,error_message\n"

    df = pd.DataFrame(records)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode()
