import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.enums import DuplicateStatus


class DuplicateCase(Base):
    """Potential duplicate enrolment between two student records."""
    __tablename__ = "duplicate_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_a_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    student_b_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    institution_a_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=True)
    institution_b_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=True)
    match_reason = Column(String(200), nullable=False)  # e.g. "apaar_hash_match", "name_dob_match"
    confidence = Column(String(20), nullable=False, default="medium")  # low/medium/high
    status = Column(String(30), nullable=False, default=DuplicateStatus.SUSPECTED.value)
    notes = Column(Text, nullable=True)
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    student_a = relationship("Student", foreign_keys=[student_a_id])
    student_b = relationship("Student", foreign_keys=[student_b_id])
    institution_a = relationship("Institution", foreign_keys=[institution_a_id])
    institution_b = relationship("Institution", foreign_keys=[institution_b_id])

    def __repr__(self):
        return f"<DuplicateCase {self.student_a_id} <-> {self.student_b_id} [{self.status}]>"
