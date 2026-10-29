from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.core.enums import InstitutionType


class InstitutionBase(BaseModel):
    name: str
    short_name: Optional[str] = None
    aicte_id: str
    institution_type: InstitutionType
    state: str
    district: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    establishment_year: Optional[int] = None


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    institution_type: Optional[InstitutionType] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    establishment_year: Optional[int] = None
    is_active: Optional[bool] = None


class InstitutionOut(InstitutionBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InstitutionSummary(BaseModel):
    id: UUID
    name: str
    short_name: Optional[str] = None
    aicte_id: str
    institution_type: InstitutionType
    state: str
    city: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


# Programme schemas
class ProgrammeBase(BaseModel):
    name: str
    code: str
    level: str
    duration_years: int = 4
    description: Optional[str] = None


class ProgrammeCreate(ProgrammeBase):
    institution_id: UUID


class ProgrammeOut(ProgrammeBase):
    id: UUID
    institution_id: UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# AcademicYear schemas
class AcademicYearBase(BaseModel):
    label: str
    start_year: int
    end_year: int
    is_current: bool = False


class AcademicYearCreate(AcademicYearBase):
    institution_id: UUID


class AcademicYearOut(AcademicYearBase):
    id: UUID
    institution_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ApprovedIntake schemas
class ApprovedIntakeBase(BaseModel):
    category: str = "general"
    approved_seats: int


class ApprovedIntakeCreate(ApprovedIntakeBase):
    programme_id: UUID
    academic_year_id: UUID


class ApprovedIntakeOut(ApprovedIntakeBase):
    id: UUID
    programme_id: UUID
    academic_year_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# Paginated response
class PaginatedInstitutions(BaseModel):
    items: List[InstitutionSummary]
    total: int
    page: int
    size: int
    pages: int
