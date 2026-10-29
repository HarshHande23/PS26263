from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID
from app.core.enums import SubmissionStatus, ValidationSeverity, ValidationStatus, DuplicateStatus


class SubmissionOut(BaseModel):
    id: UUID
    institution_id: UUID
    filename: str
    file_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    imported_rows: int
    skipped_rows: int
    intake_exceeded_rows: int
    error_summary: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ImportErrorOut(BaseModel):
    id: UUID
    submission_id: UUID
    row_number: int
    row_data: Optional[Dict[str, Any]] = None
    error_type: str
    field_name: Optional[str] = None
    error_message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ValidationFindingOut(BaseModel):
    id: UUID
    submission_id: Optional[UUID] = None
    student_id: Optional[UUID] = None
    institution_id: Optional[UUID] = None
    rule_id: str
    severity: str
    title: str
    description: Optional[str] = None
    recommendation: Optional[str] = None
    status: str
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: UUID
    institution_id: Optional[UUID] = None
    alert_type: str
    severity: str
    title: str
    message: Optional[str] = None
    status: str
    related_submission_id: Optional[UUID] = None
    related_student_id: Optional[UUID] = None
    anomaly_score: Optional[float] = None
    risk_level: Optional[str] = None
    detected_issues: Optional[List[str]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DuplicateCaseOut(BaseModel):
    id: UUID
    student_a_id: UUID
    student_b_id: UUID
    institution_a_id: Optional[UUID] = None
    institution_b_id: Optional[UUID] = None
    match_reason: str
    confidence: str
    status: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CorrectionRequestCreate(BaseModel):
    student_id: UUID
    finding_id: Optional[UUID] = None
    field_name: str
    old_value: Optional[str] = None
    new_value: str
    justification: Optional[str] = None


class CorrectionRequestOut(BaseModel):
    id: UUID
    student_id: UUID
    finding_id: Optional[UUID] = None
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    justification: Optional[str] = None
    status: str
    review_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FindingResolveRequest(BaseModel):
    resolution_note: Optional[str] = None


class PaginatedFindings(BaseModel):
    items: List[ValidationFindingOut]
    total: int
    page: int
    size: int
    pages: int
