"""
Verification API — Endpoints for APAAR verification adapter, QR code generation,
and secure public-facing verification lookup.
"""

import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.enums import UserRole, VerificationStatus
from app.models.student import Student
from app.models.institution import Institution
from app.models.programme import Programme
from app.models.academic_year import AcademicYear
from app.models.verification_request import VerificationRequest
from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.verification_provider import verification_provider
from app.schemas.verification import (
    VerificationTriggerRequest,
    VerificationResponse,
    QRGenerateResponse,
    PublicVerifyRequest,
    PublicVerifyResponse,
)

router = APIRouter()


def _get_student_with_permission(student_id: UUID, current_user: User, db: Session) -> Student:
    """Helper to ensure multi-tenant institution isolation."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    # If college admin or admission staff, enforce same institution
    if current_user.role in [UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF]:
        if str(student.institution_id) != str(current_user.institution_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot access student record belonging to another institution",
            )
    return student


@router.post("/students/{id}/verify", response_model=VerificationResponse)
def trigger_student_verification(
    id: UUID,
    payload: VerificationTriggerRequest = VerificationTriggerRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Trigger simulated APAAR verification for a student record.
    Calls the verification provider adapter and persists the result.
    """
    student = _get_student_with_permission(id, current_user, db)

    # Use provided synthetic APAAR or default 12-digit mock based on enrolment
    test_apaar = payload.apaar_id or f"12345678{str(hash(str(student.id)))[-4:]}"

    # Call provider adapter
    result = verification_provider.verify_apaar(
        apaar_id=test_apaar,
        student_name=student.full_name,
        date_of_birth=str(student.date_of_birth) if student.date_of_birth else None,
        simulate_failure_mode=payload.simulate_failure_mode,
    )

    # Update student verification state
    student.verification_status = result.status
    student.last_verified_at = datetime.now(timezone.utc)
    student.verification_notes = f"[{result.provider_name}] {result.response_code}: {result.response_message}"

    # Record VerificationRequest
    req_reference = f"VER-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
    v_req = VerificationRequest(
        student_id=student.id,
        requested_by_id=current_user.id,
        request_reference=req_reference,
        provider_mode="MOCK_SIMULATED",
        status=result.status,
        is_simulated=True,
        disclaimer=result.disclaimer,
        response_code=result.response_code,
        response_message=result.response_message,
    )
    db.add(v_req)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="student.verification.simulated",
        resource_type="Student",
        resource_id=str(student.id),
        details={
            "status": result.status.value,
            "response_code": result.response_code,
            "reference": req_reference,
            "is_simulated": True,
        },
    )
    db.add(audit)
    db.commit()
    db.refresh(student)

    return VerificationResponse(
        student_id=str(student.id),
        status=result.status,
        is_simulated=result.is_simulated,
        provider_name=result.provider_name,
        response_code=result.response_code,
        response_message=result.response_message,
        disclaimer=result.disclaimer,
        verification_timestamp=result.verification_timestamp or datetime.now(timezone.utc).isoformat(),
        matched_confidence=result.matched_identity_confidence,
    )


@router.post("/students/{id}/generate-qr", response_model=QRGenerateResponse)
def generate_student_qr_token(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate a cryptographically secure, signed opaque token for QR verification.
    The QR token contains NO sensitive student data, only an opaque reference.
    """
    student = _get_student_with_permission(id, current_user, db)

    # Generate opaque 32-byte token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    student.qr_token = token
    student.qr_token_expires_at = expires_at
    student.qr_token_revoked = False

    audit = AuditLog(
        user_id=current_user.id,
        action="student.qr_token.generated",
        resource_type="Student",
        resource_id=str(student.id),
        details={"expires_at": expires_at.isoformat()},
    )
    db.add(audit)
    db.commit()

    return QRGenerateResponse(
        token=token,
        verification_url=f"/verify/qr?token={token}",
        expires_at=expires_at,
        is_revoked=False,
        disclaimer="QR code points to a secure opaque reference. It does NOT contain raw APAAR or personal data.",
    )


@router.post("/students/{id}/revoke-qr")
def revoke_student_qr_token(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Revoke an active QR verification token."""
    student = _get_student_with_permission(id, current_user, db)
    student.qr_token_revoked = True

    audit = AuditLog(
        user_id=current_user.id,
        action="student.qr_token.revoked",
        resource_type="Student",
        resource_id=str(student.id),
        details={"revoked_at": datetime.now(timezone.utc).isoformat()},
    )
    db.add(audit)
    db.commit()

    return {"message": "QR token successfully revoked"}


@router.post("/public/verify-token", response_model=PublicVerifyResponse)
def public_verify_token(payload: PublicVerifyRequest, db: Session = Depends(get_db)):
    """
    Public-facing secure QR verification lookup.
    Exposes ONLY minimal necessary information.
    Zero raw APAAR IDs, zero internal UUIDs, zero sensitive personal records.
    """
    token = payload.token.strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token required")

    student = db.query(Student).filter(Student.qr_token == token).first()

    disclaimer = "SIMULATED VERIFICATION — Result generated via VidyaVerify Prototype Adapter. Not an official AICTE production confirmation."

    if not student:
        return PublicVerifyResponse(
            record_status="INVALID_TOKEN",
            verification_status="NOT_VERIFIED",
            verification_source="VidyaVerify Security Gateway",
            disclaimer=disclaimer,
        )

    if student.qr_token_revoked:
        return PublicVerifyResponse(
            record_status="REVOKED",
            verification_status="NOT_VERIFIED",
            verification_source="VidyaVerify Security Gateway",
            disclaimer=disclaimer,
        )

    if student.qr_token_expires_at:
        expires = student.qr_token_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            return PublicVerifyResponse(
                record_status="EXPIRED",
                verification_status="NOT_VERIFIED",
                verification_source="VidyaVerify Security Gateway",
                disclaimer=disclaimer,
            )

    # Get institution & programme names
    inst = db.query(Institution).filter(Institution.id == student.institution_id).first()
    prog = db.query(Programme).filter(Programme.id == student.programme_id).first() if student.programme_id else None
    ay = db.query(AcademicYear).filter(AcademicYear.id == student.academic_year_id).first() if student.academic_year_id else None

    # Mask name for privacy: e.g. "Aarav Kumar" -> "A. K."
    initials = " ".join([part[0] + "." for part in student.full_name.split() if part])

    v_status_label = student.verification_status.value.replace("_", " ").upper()
    if student.verification_status == VerificationStatus.VERIFIED_BY_PROVIDER:
        v_status_label = "SIMULATED — VERIFIED"

    return PublicVerifyResponse(
        record_status="FOUND",
        student_initials=initials,
        institution_name=inst.name if inst else "AICTE Affiliated Institution",
        programme_name=prog.name if prog else "Technical Programme",
        academic_year=ay.label if ay else "Current Session",
        enrolment_status=student.enrolment_status.value.capitalize(),
        verification_status=v_status_label,
        verification_source="Mock APAAR Gateway Adapter (Synthetic)",
        last_verified_at=student.last_verified_at.strftime("%Y-%m-%d %H:%M:%S UTC") if student.last_verified_at else "Pending Initial Check",
        disclaimer=disclaimer,
    )
