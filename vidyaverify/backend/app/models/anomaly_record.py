import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Boolean, JSON
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class AnomalyRecord(Base):
    """
    Persisted Isolation Forest scoring result for a student submission row.
    Maintains exact anomaly score, risk level, detected structural issues, and timestamps.
    """
    __tablename__ = "anomaly_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("upload_submissions.id"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=True, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)

    # ML Isolation Forest Output
    anomaly_score = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)
    is_anomaly = Column(Boolean, nullable=False)
    detected_issues = Column(JSON, nullable=False)
    model_version = Column(String(100), default="IsolationForest-v1-synthetic", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    submission = relationship("UploadSubmission")
    student = relationship("Student")
    institution = relationship("Institution")

    def __repr__(self):
        return f"<AnomalyRecord row={self.row_number} score={self.anomaly_score} risk={self.risk_level}>"
