// TypeScript types for the VidyaVerify application

export type UserRole =
  | 'super_admin'
  | 'aicte_admin'
  | 'college_admin'
  | 'admission_staff'
  | 'authorized_verifier'
  | 'student'

export type InstitutionType =
  | 'university'
  | 'deemed_university'
  | 'autonomous_college'
  | 'affiliated_college'
  | 'technical_institute'

export type EnrolmentStatus =
  | 'active'
  | 'inactive'
  | 'transferred'
  | 'graduated'
  | 'dropped'
  | 'suspended'

export type AdmissionCategory =
  | 'general'
  | 'obc'
  | 'sc'
  | 'st'
  | 'ews'
  | 'nri'
  | 'oci'
  | 'foreign_national'
  | 'management_quota'
  | 'sports'
  | 'defence'
  | 'ph'

export type ValidationStatus = 'open' | 'resolved' | 'dismissed' | 'under_review'
export type ValidationSeverity = 'error' | 'warning' | 'info'
export type SubmissionStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  institution_id: string | null
  created_at: string
}

export interface Institution {
  id: string
  name: string
  short_name: string | null
  aicte_id: string
  institution_type: InstitutionType
  state: string
  district: string | null
  city: string | null
  address: string | null
  pincode: string | null
  phone: string | null
  email: string | null
  website: string | null
  establishment_year: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface InstitutionSummary {
  id: string
  name: string
  short_name: string | null
  aicte_id: string
  institution_type: InstitutionType
  state: string
  city: string | null
  is_active: boolean
}

export interface Programme {
  id: string
  institution_id: string
  name: string
  code: string
  level: string
  duration_years: number
  description: string | null
  is_active: boolean
  created_at: string
}

export interface AcademicYear {
  id: string
  institution_id: string
  label: string
  start_year: number
  end_year: number
  is_current: boolean
  created_at: string
}

export interface Student {
  id: string
  apaar_id_masked: string | null
  full_name: string
  date_of_birth: string | null
  gender: string | null
  email: string | null
  phone: string | null
  institution_id: string
  programme_id: string | null
  academic_year_id: string | null
  enrolment_number: string | null
  admission_date: string | null
  admission_category: AdmissionCategory
  enrolment_status: EnrolmentStatus
  is_supernumerary: boolean
  is_nri: boolean
  is_oci: boolean
  is_foreign_national: boolean
  is_pwd: boolean
  validation_status: ValidationStatus
  created_at: string
  updated_at: string
}

export interface StudentSummary {
  id: string
  full_name: string
  enrolment_number: string | null
  apaar_id_masked: string | null
  institution_id: string
  enrolment_status: EnrolmentStatus
  admission_category: AdmissionCategory
  validation_status: ValidationStatus
}

export interface UploadSubmission {
  id: string
  institution_id: string
  filename: string
  file_type: string | null
  file_size_bytes: number | null
  status: SubmissionStatus
  total_rows: number
  valid_rows: number
  invalid_rows: number
  duplicate_rows: number
  imported_rows: number
  skipped_rows: number
  intake_exceeded_rows: number
  error_summary: string | null
  created_at: string
  completed_at: string | null
}

export interface ImportError {
  id: string
  submission_id: string
  row_number: number
  row_data: Record<string, unknown> | null
  error_type: string
  field_name: string | null
  error_message: string
  created_at: string
}

export interface ValidationFinding {
  id: string
  submission_id: string | null
  student_id: string | null
  institution_id: string | null
  rule_id: string
  severity: ValidationSeverity
  title: string
  description: string | null
  recommendation: string | null
  status: ValidationStatus
  resolved_at: string | null
  resolution_note: string | null
  created_at: string
}

export interface Alert {
  id: string
  institution_id: string | null
  alert_type: string
  severity: string
  title: string
  message: string | null
  status: string
  related_submission_id: string | null
  related_student_id: string | null
  created_at: string
}

export interface DuplicateCase {
  id: string
  student_a_id: string
  student_b_id: string
  institution_a_id: string | null
  institution_b_id: string | null
  match_reason: string
  confidence: string
  status: string
  notes: string | null
  created_at: string
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface CollegeDashboard {
  total_students: number
  active_students: number
  open_findings: number
  error_findings: number
  total_submissions: number
  suspected_duplicates: number
  open_alerts: number
}

export interface AICTEDashboard {
  total_institutions: number
  total_students: number
  active_students: number
  open_findings: number
  suspected_duplicates: number
  open_alerts: number
  total_submissions: number
  institution_summary: Array<{
    id: string
    name: string
    short_name: string | null
    active_students: number
  }>
}
