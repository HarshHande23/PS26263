import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum, Text, Integer
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.enums import InstitutionType


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(500), nullable=False, index=True)
    short_name = Column(String(50), nullable=True)
    aicte_id = Column(String(50), unique=True, nullable=False, index=True)
    institution_type = Column(SAEnum(InstitutionType), nullable=False)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    pincode = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    establishment_year = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    users = relationship("User", foreign_keys="User.institution_id", back_populates="institution")
    programmes = relationship("Programme", back_populates="institution", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="institution")
    upload_submissions = relationship("UploadSubmission", back_populates="institution")
    alerts = relationship("Alert", back_populates="institution")

    def __repr__(self):
        return f"<Institution {self.name} ({self.aicte_id})>"
