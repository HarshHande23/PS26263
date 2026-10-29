from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Query
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import io

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_roles
from app.core.enums import UserRole
from app.core.config import settings
from app.models.upload_submission import UploadSubmission
from app.models.import_error import ImportError as ImportErrorModel
from app.models.user import User
from app.schemas.upload import SubmissionOut, ImportErrorOut
from app.services.import_service import process_submission, generate_rejected_csv
import math

router = APIRouter()

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def _get_scoped_institution_id(institution_id: Optional[UUID], current_user: User) -> UUID:
    """Return institution_id, enforcing scoping for college users."""
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        if not current_user.institution_id:
            raise HTTPException(status_code=403, detail="No institution assigned to your account")
        return current_user.institution_id
    if not institution_id:
        raise HTTPException(status_code=400, detail="institution_id is required")
    return institution_id


@router.post("", response_model=SubmissionOut, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    institution_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF
    )),
):
    inst_id = _get_scoped_institution_id(institution_id, current_user)

    # Validate extension
    filename = file.filename or "upload"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    submission = UploadSubmission(
        institution_id=inst_id,
        uploaded_by_id=current_user.id,
        filename=filename,
        file_size_bytes=len(file_bytes),
    )
    db.add(submission)
    db.flush()

    submission = process_submission(submission, file_bytes, inst_id, db)
    db.commit()
    db.refresh(submission)
    return submission


@router.get("", response_model=List[SubmissionOut])
def list_submissions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    institution_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = db.query(UploadSubmission)
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        q = q.filter(UploadSubmission.institution_id == current_user.institution_id)
    elif institution_id:
        q = q.filter(UploadSubmission.institution_id == institution_id)
    return q.order_by(UploadSubmission.created_at.desc()).offset((page - 1) * size).limit(size).all()


@router.get("/{submission_id}", response_model=SubmissionOut)
def get_submission(
    submission_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    sub = db.query(UploadSubmission).filter_by(id=submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        if sub.institution_id != current_user.institution_id:
            raise HTTPException(status_code=403, detail="Access denied")
    return sub


@router.get("/{submission_id}/errors", response_model=List[ImportErrorOut])
def get_submission_errors(
    submission_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    sub = db.query(UploadSubmission).filter_by(id=submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        if sub.institution_id != current_user.institution_id:
            raise HTTPException(status_code=403, detail="Access denied")
    return db.query(ImportErrorModel).filter_by(submission_id=submission_id).all()


@router.get("/{submission_id}/rejected-export")
def export_rejected_rows(
    submission_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Download a CSV of all rejected rows for this submission."""
    sub = db.query(UploadSubmission).filter_by(id=submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        if sub.institution_id != current_user.institution_id:
            raise HTTPException(status_code=403, detail="Access denied")

    csv_bytes = generate_rejected_csv(submission_id, db)
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=rejected_rows_{submission_id}.csv"},
    )


@router.get("/template/download")
def download_template():
    """Return the CSV import template."""
    header = (
        "full_name,apaar_id,date_of_birth,gender,email,phone,"
        "enrolment_number,programme_code,academic_year,admission_date,"
        "admission_category,is_supernumerary,is_nri,is_oci,is_foreign_national,is_pwd\n"
    )
    sample = (
        "Aarav Kumar,123456789012,2002-05-15,Male,aarav@example.com,9876543210,"
        "2024CS001,BTECH-CS,2024-25,2024-08-01,general,false,false,false,false,false\n"
    )
    content = (header + sample).encode()
    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=student_import_template.csv"},
    )
