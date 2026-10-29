from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from app.core.enums import EnrolmentStatus, AdmissionCategory, ValidationStatus, VerificationStatus


class StudentBase(BaseModel):
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    institution_id: UUID
    programme_id: Optional[UUID] = None
    academic_year_id: Optional[UUID] = None
    enrolment_number: Optional[str] = None
    admission_date: Optional[date] = None
    admission_category: AdmissionCategory = AdmissionCategory.GENERAL
    enrolment_status: EnrolmentStatus = EnrolmentStatus.ACTIVE
    is_supernumerary: bool = False
    is_nri: bool = False
    is_oci: bool = False
    is_foreign_national: bool = False
    is_pwd: bool = False


class StudentCreate(StudentBase):
    # Raw APAAR ID submitted by user — will be hashed before storage
    apaar_id: Optional[str] = None
    aadhaar_last4: Optional[str] = None


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    programme_id: Optional[UUID] = None
    academic_year_id: Optional[UUID] = None
    enrolment_number: Optional[str] = None
    admission_date: Optional[date] = None
    admission_category: Optional[AdmissionCategory] = None
    enrolment_status: Optional[EnrolmentStatus] = None
    is_supernumerary: Optional[bool] = None
    is_nri: Optional[bool] = None
    is_oci: Optional[bool] = None
    is_foreign_national: Optional[bool] = None
    is_pwd: Optional[bool] = None
    apaar_id: Optional[str] = None  # hashed on update


class StudentOut(BaseModel):
    id: UUID
    apaar_id_masked: Optional[str] = None
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    institution_id: UUID
    programme_id: Optional[UUID] = None
    academic_year_id: Optional[UUID] = None
    enrolment_number: Optional[str] = None
    admission_date: Optional[date] = None
    admission_category: AdmissionCategory
    enrolment_status: EnrolmentStatus
    is_supernumerary: bool
    is_nri: bool
    is_oci: bool
    is_foreign_national: bool
    is_pwd: bool
    validation_status: ValidationStatus
    verification_status: VerificationStatus = VerificationStatus.NOT_CHECKED
    last_verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    qr_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StudentSummary(BaseModel):
    id: UUID
    full_name: str
    enrolment_number: Optional[str] = None
    apaar_id_masked: Optional[str] = None
    institution_id: UUID
    enrolment_status: EnrolmentStatus
    admission_category: AdmissionCategory
    validation_status: ValidationStatus
    verification_status: VerificationStatus = VerificationStatus.NOT_CHECKED

    model_config = {"from_attributes": True}


class PaginatedStudents(BaseModel):
    items: List[StudentSummary]
    total: int
    page: int
    size: int
    pages: int


class EnrolmentHistoryOut(BaseModel):
    id: UUID
    student_id: UUID
    institution_id: UUID
    status: str
    effective_date: Optional[date] = None
    reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
