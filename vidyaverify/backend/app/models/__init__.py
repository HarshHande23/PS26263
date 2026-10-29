from app.core.database import Base  # noqa: F401 - imported for Alembic autogenerate

from app.models.user import User  # noqa
from app.models.institution import Institution  # noqa
from app.models.programme import Programme  # noqa
from app.models.academic_year import AcademicYear  # noqa
from app.models.approved_intake import ApprovedIntake  # noqa
from app.models.student import Student  # noqa
from app.models.enrolment_history import EnrolmentHistory  # noqa
from app.models.upload_submission import UploadSubmission  # noqa
from app.models.import_error import ImportError  # noqa
from app.models.validation_finding import ValidationFinding  # noqa
from app.models.duplicate_case import DuplicateCase  # noqa
from app.models.alert import Alert  # noqa
from app.models.audit_log import AuditLog  # noqa
from app.models.correction_request import CorrectionRequest  # noqa
from app.models.verification_request import VerificationRequest  # noqa
