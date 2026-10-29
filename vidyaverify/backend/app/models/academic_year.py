import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, UniqueConstraint
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False, index=True)
    label = Column(String(20), nullable=False)  # e.g. "2023-24"
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=False)
    is_current = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("institution_id", "label", name="uq_academic_year_institution_label"),
    )

    institution = relationship("Institution", foreign_keys=[institution_id])
    approved_intakes = relationship("ApprovedIntake", back_populates="academic_year", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="academic_year")

    def __repr__(self):
        return f"<AcademicYear {self.label}>"
