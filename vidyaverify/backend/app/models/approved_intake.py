import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.enums import AdmissionCategory


class ApprovedIntake(Base):
    """Approved intake per programme per academic year per category."""
    __tablename__ = "approved_intakes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    programme_id = Column(UUID(as_uuid=True), ForeignKey("programmes.id"), nullable=False, index=True)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False, default="general")  # stores AdmissionCategory value
    approved_seats = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("programme_id", "academic_year_id", "category",
                         name="uq_intake_programme_year_category"),
    )

    programme = relationship("Programme", back_populates="approved_intakes")
    academic_year = relationship("AcademicYear", back_populates="approved_intakes")

    def __repr__(self):
        return f"<ApprovedIntake {self.programme_id}/{self.category}: {self.approved_seats}>"
