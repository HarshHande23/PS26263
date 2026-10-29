import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.enums import ValidationSeverity, ValidationStatus


class ValidationFinding(Base):
    __tablename__ = "validation_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("upload_submissions.id"), nullable=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=True, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=True, index=True)

    rule_id = Column(String(100), nullable=False)       # e.g. "RULE_MISSING_APAAR"
    severity = Column(String(20), nullable=False, default=ValidationSeverity.WARNING.value)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default=ValidationStatus.OPEN.value)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    submission = relationship("UploadSubmission", back_populates="validation_findings")
    student = relationship("Student", back_populates="validation_findings")
    institution = relationship("Institution", foreign_keys=[institution_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])

    def __repr__(self):
        return f"<ValidationFinding {self.rule_id} [{self.severity}] {self.status}>"
