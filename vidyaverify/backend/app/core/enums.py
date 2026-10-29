from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    SUPER_ADMIN = "super_admin"
    AICTE_ADMIN = "aicte_admin"
    COLLEGE_ADMIN = "college_admin"
    ADMISSION_STAFF = "admission_staff"
    AUTHORIZED_VERIFIER = "authorized_verifier"
    STUDENT = "student"


class InstitutionType(str, PyEnum):
    UNIVERSITY = "university"
    DEEMED_UNIVERSITY = "deemed_university"
    AUTONOMOUS_COLLEGE = "autonomous_college"
    AFFILIATED_COLLEGE = "affiliated_college"
    TECHNICAL_INSTITUTE = "technical_institute"


class ProgrammeLevel(str, PyEnum):
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    DIPLOMA = "diploma"
    PHD = "phd"


class EnrolmentStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRANSFERRED = "transferred"
    GRADUATED = "graduated"
    DROPPED = "dropped"
    SUSPENDED = "suspended"


class AdmissionCategory(str, PyEnum):
    GENERAL = "general"
    OBC = "obc"
    SC = "sc"
    ST = "st"
    EWS = "ews"
    NRI = "nri"
    OCI = "oci"
    FOREIGN_NATIONAL = "foreign_national"
    MANAGEMENT_QUOTA = "management_quota"
    SPORTS = "sports"
    DEFENCE = "defence"
    PH = "ph"  # Persons with Handicap


class ValidationSeverity(str, PyEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationStatus(str, PyEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"
    UNDER_REVIEW = "under_review"


class SubmissionStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DuplicateStatus(str, PyEnum):
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"
    UNDER_REVIEW = "under_review"


class AlertStatus(str, PyEnum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    AWAITING_INSTITUTION_CORRECTION = "awaiting_institution_correction"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class VerificationStatus(str, PyEnum):
    NOT_CHECKED = "not_checked"
    FORMAT_VALID = "format_valid"
    PENDING_EXTERNAL_VERIFICATION = "pending_external_verification"
    VERIFIED_BY_PROVIDER = "verified_by_provider"
    NOT_VERIFIED = "not_verified"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"


class CorrectionStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
