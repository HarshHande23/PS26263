import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Date
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.enums import EnrolmentStatus


class EnrolmentHistory(Base):
    __tablename__ = "enrolment_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    programme_id = Column(UUID(as_uuid=True), ForeignKey("programmes.id"), nullable=True)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=True)
    status = Column(String(50), nullable=False)
    effective_date = Column(Date, nullable=True)
    reason = Column(Text, nullable=True)
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    student = relationship("Student", back_populates="enrolment_history")
    institution = relationship("Institution", foreign_keys=[institution_id])
    changed_by = relationship("User", foreign_keys=[changed_by_id])

    def __repr__(self):
        return f"<EnrolmentHistory student={self.student_id} status={self.status}>"
