import uuid
from datetime import datetime, timezone, date
from sqlalchemy import (Column, String, Boolean, DateTime, Date,
                        Enum as SAEnum, ForeignKey, Text, Index)
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.enums import EnrolmentStatus, AdmissionCategory, ValidationStatus, VerificationStatus


class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Core identity — APAAR ID is NOT the primary key
    # Stored hashed/masked; never log raw value
    apaar_id_hash = Column(String(255), nullable=True, index=True)  # SHA256 of APAAR ID for dedup
    apaar_id_masked = Column(String(50), nullable=True)  # e.g. "XXXX-XXXX-1234"

    # Personal info
    full_name = Column(String(500), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    aadhaar_masked = Column(String(20), nullable=True)  # Last 4 digits only

    # Institution association
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False, index=True)
    programme_id = Column(UUID(as_uuid=True), ForeignKey("programmes.id"), nullable=True, index=True)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=True, index=True)

    # Enrolment details
    enrolment_number = Column(String(100), nullable=True, index=True)
    admission_date = Column(Date, nullable=True)
    admission_category = Column(SAEnum(AdmissionCategory), nullable=False, default=AdmissionCategory.GENERAL)
    enrolment_status = Column(SAEnum(EnrolmentStatus), nullable=False, default=EnrolmentStatus.ACTIVE)

    # Special classifications
    is_supernumerary = Column(Boolean, default=False, nullable=False)
    is_nri = Column(Boolean, default=False, nullable=False)
    is_oci = Column(Boolean, default=False, nullable=False)
    is_foreign_national = Column(Boolean, default=False, nullable=False)
    is_pwd = Column(Boolean, default=False, nullable=False)

    # Validation state
    validation_status = Column(SAEnum(ValidationStatus), nullable=False, default=ValidationStatus.OPEN)

    # Verification state
    verification_status = Column(SAEnum(VerificationStatus), nullable=False, default=VerificationStatus.NOT_CHECKED)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_notes = Column(String(500), nullable=True)

    # QR Verification Token
    qr_token = Column(String(255), nullable=True, unique=True, index=True)
    qr_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    qr_token_revoked = Column(Boolean, default=False, nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    institution = relationship("Institution", back_populates="students")
    programme = relationship("Programme", back_populates="students")
    academic_year = relationship("AcademicYear", back_populates="students")
    enrolment_history = relationship("EnrolmentHistory", back_populates="student", cascade="all, delete-orphan")
    validation_findings = relationship("ValidationFinding", back_populates="student")
    correction_requests = relationship("CorrectionRequest", back_populates="student")
    verification_requests = relationship("VerificationRequest", back_populates="student", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_students_institution_status", "institution_id", "enrolment_status"),
        Index("ix_students_apaar_hash", "apaar_id_hash"),
    )

    def __repr__(self):
        return f"<Student {self.full_name} ({self.enrolment_number})>"
