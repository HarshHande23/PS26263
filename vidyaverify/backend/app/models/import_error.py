import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, JSON
from app.core.database import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class ImportError(Base):
    """Row-level errors from a file upload submission."""
    __tablename__ = "import_errors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("upload_submissions.id"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    row_data = Column(JSON, nullable=True)  # Original row values (no APAAR hash raw)
    error_type = Column(String(100), nullable=False)  # e.g. "missing_field", "duplicate"
    field_name = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    submission = relationship("UploadSubmission", back_populates="import_errors")

    def __repr__(self):
        return f"<ImportError row={self.row_number} type={self.error_type}>"
