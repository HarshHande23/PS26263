import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, Text
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.enums import ProgrammeLevel


class Programme(Base):
    __tablename__ = "programmes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    code = Column(String(50), nullable=False)
    level = Column(SAEnum(ProgrammeLevel), nullable=False)
    duration_years = Column(Integer, nullable=False, default=4)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    institution = relationship("Institution", back_populates="programmes")
    approved_intakes = relationship("ApprovedIntake", back_populates="programme", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="programme")

    def __repr__(self):
        return f"<Programme {self.code} - {self.name}>"
