from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.enums import VerificationStatus


class VerificationTriggerRequest(BaseModel):
    apaar_id: Optional[str] = None
    simulate_failure_mode: Optional[str] = None  # "timeout", "unavailable", "manual_review", "not_found"


class VerificationResponse(BaseModel):
    student_id: str
    status: VerificationStatus
    is_simulated: bool
    provider_name: str
    response_code: str
    response_message: str
    disclaimer: str
    verification_timestamp: str
    matched_confidence: Optional[str] = None


class QRGenerateResponse(BaseModel):
    token: str
    verification_url: str
    expires_at: datetime
    is_revoked: bool
    disclaimer: str


class PublicVerifyRequest(BaseModel):
    token: str


class PublicVerifyResponse(BaseModel):
    record_status: str
    student_initials: Optional[str] = None
    institution_name: Optional[str] = None
    programme_name: Optional[str] = None
    academic_year: Optional[str] = None
    enrolment_status: Optional[str] = None
    verification_status: str
    verification_source: str
    last_verified_at: Optional[str] = None
    disclaimer: str
