import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, BigInteger, Text
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.enums import SubmissionStatus


class UploadSubmission(Base):
    __tablename__ = "upload_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False, index=True)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)
    file_type = Column(String(20), nullable=True)  # "csv" or "xlsx"
    status = Column(String(50), nullable=False, default=SubmissionStatus.PENDING.value)
    total_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)
    invalid_rows = Column(Integer, default=0)
    duplicate_rows = Column(Integer, default=0)
    imported_rows = Column(Integer, default=0)
    skipped_rows = Column(Integer, default=0)
    intake_exceeded_rows = Column(Integer, default=0)
    error_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    institution = relationship("Institution", back_populates="upload_submissions")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    import_errors = relationship("ImportError", back_populates="submission", cascade="all, delete-orphan")
    validation_findings = relationship("ValidationFinding", back_populates="submission")

    def __repr__(self):
        return f"<UploadSubmission {self.filename} ({self.status})>"
