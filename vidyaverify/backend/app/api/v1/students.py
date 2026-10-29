from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import math
import hashlib

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_roles
from app.core.enums import UserRole
from app.models.student import Student
from app.models.enrolment_history import EnrolmentHistory
from app.models.user import User
from app.schemas.student import (
    StudentCreate, StudentUpdate, StudentOut, StudentSummary,
    PaginatedStudents, EnrolmentHistoryOut,
)
from app.services.validation_engine import validation_engine, hash_apaar, mask_apaar

router = APIRouter()


def _assert_institution_access(institution_id: UUID, current_user: User) -> None:
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        if current_user.institution_id != institution_id:
            raise HTTPException(status_code=403, detail="Access denied to this institution's students")
    if current_user.role == UserRole.STUDENT:
        # Students can only see their own record via /me endpoint
        raise HTTPException(status_code=403, detail="Students cannot browse the directory")
    if current_user.role == UserRole.AUTHORIZED_VERIFIER:
        # Verifiers can search but not see full details — handled per endpoint
        pass


@router.get("", response_model=PaginatedStudents)
def list_students(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    institution_id: Optional[UUID] = None,
    search: Optional[str] = None,
    enrolment_status: Optional[str] = None,
    admission_category: Optional[str] = None,
    validation_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Access denied")

    q = db.query(Student)

    # Scope college users to their institution
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        q = q.filter(Student.institution_id == current_user.institution_id)
    elif institution_id:
        q = q.filter(Student.institution_id == institution_id)

    if search:
        q = q.filter(
            Student.full_name.ilike(f"%{search}%") |
            Student.enrolment_number.ilike(f"%{search}%")
        )
    if enrolment_status:
        q = q.filter(Student.enrolment_status == enrolment_status)
    if admission_category:
        q = q.filter(Student.admission_category == admission_category)
    if validation_status:
        q = q.filter(Student.validation_status == validation_status)

    total = q.count()
    items = q.order_by(Student.full_name).offset((page - 1) * size).limit(size).all()
    return PaginatedStudents(
        items=items, total=total, page=page, size=size, pages=math.ceil(total / size) if total else 0
    )


@router.get("/{student_id}", response_model=StudentOut)
def get_student(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Students can only see their own record
    if current_user.role == UserRole.STUDENT:
        if str(current_user.student_id) != str(student_id):
            raise HTTPException(status_code=403, detail="Access denied")

    # College users scoped to institution
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        if current_user.institution_id != student.institution_id:
            raise HTTPException(status_code=403, detail="Access denied")

    return student


@router.post("", response_model=StudentOut, status_code=201)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF
    )),
):
    _assert_institution_access(payload.institution_id, current_user)

    # Hash APAAR ID — never store raw
    apaar_hash = None
    apaar_masked = None
    if payload.apaar_id:
        apaar_hash = hash_apaar(payload.apaar_id)
        apaar_masked = mask_apaar(payload.apaar_id)

    student = Student(
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        email=payload.email,
        phone=payload.phone,
        institution_id=payload.institution_id,
        programme_id=payload.programme_id,
        academic_year_id=payload.academic_year_id,
        enrolment_number=payload.enrolment_number,
        admission_date=payload.admission_date,
        admission_category=payload.admission_category,
        enrolment_status=payload.enrolment_status,
        is_supernumerary=payload.is_supernumerary,
        is_nri=payload.is_nri,
        is_oci=payload.is_oci,
        is_foreign_national=payload.is_foreign_national,
        is_pwd=payload.is_pwd,
        apaar_id_hash=apaar_hash,
        apaar_id_masked=apaar_masked,
        aadhaar_masked=f"XXXX {payload.aadhaar_last4}" if payload.aadhaar_last4 else None,
        created_by_id=current_user.id,
    )
    db.add(student)

    # Validate and create findings
    row_data = payload.model_dump()
    row_data["apaar_id"] = payload.apaar_id or ""
    findings = validation_engine.validate_row(row_data, 1)
    if findings:
        validation_engine.save_findings(
            findings, db,
            student_id=student.id,
            institution_id=payload.institution_id,
        )

    # Add enrolment history entry
    history = EnrolmentHistory(
        student_id=student.id,
        institution_id=payload.institution_id,
        programme_id=payload.programme_id,
        academic_year_id=payload.academic_year_id,
        status=payload.enrolment_status.value,
        reason="Initial enrolment",
        changed_by_id=current_user.id,
    )
    db.add(history)

    db.commit()
    db.refresh(student)
    return student


@router.put("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: UUID,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF
    )),
):
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    _assert_institution_access(student.institution_id, current_user)

    update_data = payload.model_dump(exclude_none=True)
    apaar_raw = update_data.pop("apaar_id", None)
    if apaar_raw:
        update_data["apaar_id_hash"] = hash_apaar(apaar_raw)
        update_data["apaar_id_masked"] = mask_apaar(apaar_raw)

    # Track enrolment status changes
    old_status = student.enrolment_status
    for field, value in update_data.items():
        setattr(student, field, value)

    if payload.enrolment_status and payload.enrolment_status != old_status:
        history = EnrolmentHistory(
            student_id=student.id,
            institution_id=student.institution_id,
            status=payload.enrolment_status.value,
            reason="Status updated via API",
            changed_by_id=current_user.id,
        )
        db.add(history)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN)),
):
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()


@router.get("/{student_id}/history", response_model=List[EnrolmentHistoryOut])
def get_enrolment_history(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        if current_user.institution_id != student.institution_id:
            raise HTTPException(status_code=403, detail="Access denied")

    return db.query(EnrolmentHistory).filter_by(student_id=student_id).order_by(
        EnrolmentHistory.created_at.desc()
    ).all()
