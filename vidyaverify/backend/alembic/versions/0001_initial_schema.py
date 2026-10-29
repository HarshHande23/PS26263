"""Initial schema - all tables

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enums
    userrole = postgresql.ENUM(
        'super_admin', 'aicte_admin', 'college_admin', 'admission_staff',
        'authorized_verifier', 'student', name='userrole'
    )
    institutiontype = postgresql.ENUM(
        'university', 'deemed_university', 'autonomous_college',
        'affiliated_college', 'technical_institute', name='institutiontype'
    )
    programmelevel = postgresql.ENUM(
        'undergraduate', 'postgraduate', 'diploma', 'phd', name='programmelevel'
    )
    enrolmentstatus = postgresql.ENUM(
        'active', 'inactive', 'transferred', 'graduated', 'dropped', 'suspended',
        name='enrolmentstatus'
    )
    admissioncategory = postgresql.ENUM(
        'general', 'obc', 'sc', 'st', 'ews', 'nri', 'oci', 'foreign_national',
        'management_quota', 'sports', 'defence', 'ph', name='admissioncategory'
    )
    validationstatus = postgresql.ENUM(
        'open', 'resolved', 'dismissed', 'under_review', name='validationstatus'
    )

    userrole.create(op.get_bind(), checkfirst=True)
    institutiontype.create(op.get_bind(), checkfirst=True)
    programmelevel.create(op.get_bind(), checkfirst=True)
    enrolmentstatus.create(op.get_bind(), checkfirst=True)
    admissioncategory.create(op.get_bind(), checkfirst=True)
    validationstatus.create(op.get_bind(), checkfirst=True)

    # institutions
    op.create_table(
        'institutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('short_name', sa.String(50), nullable=True),
        sa.Column('aicte_id', sa.String(50), nullable=False),
        sa.Column('institution_type', sa.String(50), nullable=False),
        sa.Column('state', sa.String(100), nullable=False),
        sa.Column('district', sa.String(100), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('pincode', sa.String(10), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('establishment_year', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('aicte_id'),
    )
    op.create_index('ix_institutions_name', 'institutions', ['name'])
    op.create_index('ix_institutions_aicte_id', 'institutions', ['aicte_id'])

    # users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # programmes
    op.create_table(
        'programmes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('level', sa.String(30), nullable=False),
        sa.Column('duration_years', sa.Integer, nullable=False, default=4),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # academic_years
    op.create_table(
        'academic_years',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('label', sa.String(20), nullable=False),
        sa.Column('start_year', sa.Integer, nullable=False),
        sa.Column('end_year', sa.Integer, nullable=False),
        sa.Column('is_current', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('institution_id', 'label', name='uq_academic_year_institution_label'),
    )

    # approved_intakes
    op.create_table(
        'approved_intakes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('programme_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(50), nullable=False, default='general'),
        sa.Column('approved_seats', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['programme_id'], ['programmes.id']),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('programme_id', 'academic_year_id', 'category',
                            name='uq_intake_programme_year_category'),
    )

    # students
    op.create_table(
        'students',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('apaar_id_hash', sa.String(255), nullable=True),
        sa.Column('apaar_id_masked', sa.String(50), nullable=True),
        sa.Column('full_name', sa.String(500), nullable=False),
        sa.Column('date_of_birth', sa.Date, nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('aadhaar_masked', sa.String(20), nullable=True),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('programme_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('enrolment_number', sa.String(100), nullable=True),
        sa.Column('admission_date', sa.Date, nullable=True),
        sa.Column('admission_category', sa.String(50), nullable=False, default='general'),
        sa.Column('enrolment_status', sa.String(30), nullable=False, default='active'),
        sa.Column('is_supernumerary', sa.Boolean, nullable=False, default=False),
        sa.Column('is_nri', sa.Boolean, nullable=False, default=False),
        sa.Column('is_oci', sa.Boolean, nullable=False, default=False),
        sa.Column('is_foreign_national', sa.Boolean, nullable=False, default=False),
        sa.Column('is_pwd', sa.Boolean, nullable=False, default=False),
        sa.Column('validation_status', sa.String(30), nullable=False, default='open'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id']),
        sa.ForeignKeyConstraint(['programme_id'], ['programmes.id']),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_students_institution_status', 'students', ['institution_id', 'enrolment_status'])
    op.create_index('ix_students_apaar_hash', 'students', ['apaar_id_hash'])
    op.create_index('ix_students_enrolment_number', 'students', ['enrolment_number'])

    # enrolment_history
    op.create_table(
        'enrolment_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('programme_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('effective_date', sa.Date, nullable=True),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('changed_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id']),
        sa.ForeignKeyConstraint(['programme_id'], ['programmes.id']),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id']),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_enrolment_history_student', 'enrolment_history', ['student_id'])

    # upload_submissions
    op.create_table(
        'upload_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger, nullable=True),
        sa.Column('file_type', sa.String(20), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('total_rows', sa.Integer, default=0),
        sa.Column('valid_rows', sa.Integer, default=0),
        sa.Column('invalid_rows', sa.Integer, default=0),
        sa.Column('duplicate_rows', sa.Integer, default=0),
        sa.Column('imported_rows', sa.Integer, default=0),
        sa.Column('skipped_rows', sa.Integer, default=0),
        sa.Column('intake_exceeded_rows', sa.Integer, default=0),
        sa.Column('error_summary', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id']),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # import_errors
    op.create_table(
        'import_errors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('row_number', sa.Integer, nullable=False),
        sa.Column('row_data', postgresql.JSON, nullable=True),
        sa.Column('error_type', sa.String(100), nullable=False),
        sa.Column('field_name', sa.String(100), nullable=True),
        sa.Column('error_message', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['submission_id'], ['upload_submissions.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_import_errors_submission', 'import_errors', ['submission_id'])

    # validation_findings
    op.create_table(
        'validation_findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rule_id', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, default='warning'),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('recommendation', sa.Text, nullable=True),
        sa.Column('status', sa.String(30), nullable=False, default='open'),
        sa.Column('resolved_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_note', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['submission_id'], ['upload_submissions.id']),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id']),
        sa.ForeignKeyConstraint(['resolved_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # duplicate_cases
    op.create_table(
        'duplicate_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_a_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_b_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institution_a_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('institution_b_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('match_reason', sa.String(200), nullable=False),
        sa.Column('confidence', sa.String(20), nullable=False, default='medium'),
        sa.Column('status', sa.String(30), nullable=False, default='suspected'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('reviewed_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['student_a_id'], ['students.id']),
        sa.ForeignKeyConstraint(['student_b_id'], ['students.id']),
        sa.ForeignKeyConstraint(['institution_a_id'], ['institutions.id']),
        sa.ForeignKeyConstraint(['institution_b_id'], ['institutions.id']),
        sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # alerts
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institution_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('alert_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, default='warning'),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('message', sa.Text, nullable=True),
        sa.Column('status', sa.String(30), nullable=False, default='open'),
        sa.Column('related_submission_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_student_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('acknowledged_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id']),
        sa.ForeignKeyConstraint(['related_submission_id'], ['upload_submissions.id']),
        sa.ForeignKeyConstraint(['related_student_id'], ['students.id']),
        sa.ForeignKeyConstraint(['acknowledged_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(200), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=True),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('details', postgresql.JSON, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_logs_user', 'audit_logs', ['user_id'])

    # correction_requests
    op.create_table(
        'correction_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('finding_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('requested_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_name', sa.String(100), nullable=False),
        sa.Column('old_value', sa.Text, nullable=True),
        sa.Column('new_value', sa.Text, nullable=True),
        sa.Column('justification', sa.Text, nullable=True),
        sa.Column('status', sa.String(30), nullable=False, default='pending'),
        sa.Column('reviewed_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_note', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.ForeignKeyConstraint(['finding_id'], ['validation_findings.id']),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # Add FK from users.student_id to students
    op.create_foreign_key(
        'fk_users_student_id', 'users', 'students', ['student_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_student_id', 'users', type_='foreignkey')
    op.drop_table('correction_requests')
    op.drop_table('audit_logs')
    op.drop_table('alerts')
    op.drop_table('duplicate_cases')
    op.drop_table('validation_findings')
    op.drop_table('import_errors')
    op.drop_table('upload_submissions')
    op.drop_table('enrolment_history')
    op.drop_table('students')
    op.drop_table('approved_intakes')
    op.drop_table('academic_years')
    op.drop_table('programmes')
    op.drop_table('users')
    op.drop_table('institutions')
