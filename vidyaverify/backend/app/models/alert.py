import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, JSON
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.enums import AlertStatus


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=True, index=True)
    alert_type = Column(String(100), nullable=False)  # e.g. "intake_exceeded", "duplicate_found", "ml_anomaly"
    severity = Column(String(20), nullable=False, default="warning")
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default=AlertStatus.OPEN.value)
    related_submission_id = Column(UUID(as_uuid=True), ForeignKey("upload_submissions.id"), nullable=True)
    related_student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=True)
    acknowledged_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # ML Isolation Forest Anomaly Metadata
    anomaly_score = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)
    detected_issues = Column(JSON, nullable=True)

    institution = relationship("Institution", back_populates="alerts")
    submission = relationship("UploadSubmission", foreign_keys=[related_submission_id])
    student = relationship("Student", foreign_keys=[related_student_id])
    acknowledged_by = relationship("User", foreign_keys=[acknowledged_by_id])

    def __repr__(self):
        return f"<Alert {self.alert_type} [{self.status}]>"
