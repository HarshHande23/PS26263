import { apiClient } from './client'
import type {
  User, Institution, InstitutionSummary, Student, StudentSummary,
  UploadSubmission, ImportError, ValidationFinding, Alert, DuplicateCase,
  Programme, AcademicYear, Paginated, CollegeDashboard, AICTEDashboard
} from '@/types'

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  login: async (email: string, password: string): Promise<{ access_token: string; user: User }> => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    const res = await apiClient.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return res.data
  },
  me: async (): Promise<User> => {
    const res = await apiClient.get('/auth/me')
    return res.data
  },
}

// ── Institutions ──────────────────────────────────────────────────────────────
export const institutionsApi = {
  list: async (params?: { page?: number; size?: number; search?: string; state?: string }): Promise<Paginated<InstitutionSummary>> => {
    const res = await apiClient.get('/institutions', { params })
    return res.data
  },
  get: async (id: string): Promise<Institution> => {
    const res = await apiClient.get(`/institutions/${id}`)
    return res.data
  },
  create: async (data: Partial<Institution>): Promise<Institution> => {
    const res = await apiClient.post('/institutions', data)
    return res.data
  },
  update: async (id: string, data: Partial<Institution>): Promise<Institution> => {
    const res = await apiClient.put(`/institutions/${id}`, data)
    return res.data
  },
  programmes: async (id: string): Promise<Programme[]> => {
    const res = await apiClient.get(`/institutions/${id}/programmes`)
    return res.data
  },
  academicYears: async (id: string): Promise<AcademicYear[]> => {
    const res = await apiClient.get(`/institutions/${id}/academic-years`)
    return res.data
  },
  intake: async (id: string, params?: { programme_id?: string; academic_year_id?: string }) => {
    const res = await apiClient.get(`/institutions/${id}/intake`, { params })
    return res.data
  },
}

// ── Students ──────────────────────────────────────────────────────────────────
export const studentsApi = {
  list: async (params?: {
    page?: number; size?: number; institution_id?: string;
    search?: string; enrolment_status?: string; validation_status?: string;
  }): Promise<Paginated<StudentSummary>> => {
    const res = await apiClient.get('/students', { params })
    return res.data
  },
  get: async (id: string): Promise<Student> => {
    const res = await apiClient.get(`/students/${id}`)
    return res.data
  },
  create: async (data: Partial<Student> & { apaar_id?: string }): Promise<Student> => {
    const res = await apiClient.post('/students', data)
    return res.data
  },
  update: async (id: string, data: Partial<Student> & { apaar_id?: string }): Promise<Student> => {
    const res = await apiClient.put(`/students/${id}`, data)
    return res.data
  },
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/students/${id}`)
  },
  history: async (id: string) => {
    const res = await apiClient.get(`/students/${id}/history`)
    return res.data
  },
}

// ── Uploads ───────────────────────────────────────────────────────────────────
export const uploadsApi = {
  upload: async (file: File, institution_id?: string): Promise<UploadSubmission> => {
    const form = new FormData()
    form.append('file', file)
    const params = institution_id ? { institution_id } : {}
    const res = await apiClient.post('/uploads', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params,
    })
    return res.data
  },
  list: async (params?: { institution_id?: string; page?: number; size?: number }): Promise<UploadSubmission[]> => {
    const res = await apiClient.get('/uploads', { params })
    return res.data
  },
  get: async (id: string): Promise<UploadSubmission> => {
    const res = await apiClient.get(`/uploads/${id}`)
    return res.data
  },
  errors: async (id: string): Promise<ImportError[]> => {
    const res = await apiClient.get(`/uploads/${id}/errors`)
    return res.data
  },
  exportRejectedRows: async (id: string): Promise<Blob> => {
    const res = await apiClient.get(`/uploads/${id}/rejected-export`, {
      responseType: 'blob',
    })
    return res.data
  },
  rejectedExportUrl: (id: string) => {
    const token = localStorage.getItem('access_token')
    return `${apiClient.defaults.baseURL}/uploads/${id}/rejected-export${token ? `?token=${encodeURIComponent(token)}` : ''}`
  },
  templateUrl: () => `${apiClient.defaults.baseURL}/uploads/template/download`,
}

// ── Findings ──────────────────────────────────────────────────────────────────
export const findingsApi = {
  list: async (params?: {
    institution_id?: string; severity?: string; status?: string;
    rule_id?: string; page?: number; size?: number;
  }): Promise<Paginated<ValidationFinding>> => {
    const res = await apiClient.get('/findings', { params })
    return res.data
  },
  resolve: async (id: string, note?: string) => {
    const res = await apiClient.post(`/findings/${id}/resolve`, { resolution_note: note })
    return res.data
  },
  dismiss: async (id: string) => {
    const res = await apiClient.post(`/findings/${id}/dismiss`)
    return res.data
  },
  duplicates: async (params?: { institution_id?: string; status?: string }): Promise<DuplicateCase[]> => {
    const res = await apiClient.get('/findings/duplicates', { params })
    return res.data
  },
  reviewDuplicate: async (id: string, status: string, notes?: string): Promise<DuplicateCase> => {
    const res = await apiClient.post(`/findings/duplicates/${id}/review`, { status, notes })
    return res.data
  },
}

// ── Alerts ────────────────────────────────────────────────────────────────────
export const alertsApi = {
  list: async (params?: { institution_id?: string; status?: string; alert_type?: string; limit?: number }): Promise<Alert[]> => {
    const res = await apiClient.get('/alerts', { params })
    return res.data
  },
  acknowledge: async (id: string): Promise<Alert> => {
    const res = await apiClient.post(`/alerts/${id}/acknowledge`)
    return res.data
  },
  transition: async (id: string, new_status: string, resolution_notes?: string): Promise<Alert> => {
    const res = await apiClient.post(`/alerts/${id}/transition`, { new_status, resolution_notes })
    return res.data
  },
}

// ── Verification ──────────────────────────────────────────────────────────────
export const verificationApi = {
  verifyStudent: async (studentId: string, forceSimulatedOutcome?: string): Promise<any> => {
    const res = await apiClient.post(
      `/verification/students/${studentId}/verify`,
      forceSimulatedOutcome ? { force_simulated_outcome: forceSimulatedOutcome } : {}
    )
    return res.data
  },
  generateQr: async (studentId: string): Promise<{ student_id: string; qr_token: string; expires_at: string; verify_url: string }> => {
    const res = await apiClient.post(`/verification/students/${studentId}/generate-qr`)
    return res.data
  },
  publicVerifyToken: async (token: string): Promise<any> => {
    const res = await apiClient.get(`/verification/public/verify-token`, { params: { token } })
    return res.data
  },
  history: async (studentId: string): Promise<any[]> => {
    const res = await apiClient.get(`/verification/students/${studentId}/history`)
    return res.data
  },
}

// ── Reports & Compliance ──────────────────────────────────────────────────────
export const reportsApi = {
  enrolmentSummary: async (format: 'json' | 'csv' = 'json') => {
    const res = await apiClient.get('/reports/enrolment-summary', { params: { format } })
    return res.data
  },
  intakeDiscrepancies: async (format: 'json' | 'csv' = 'json') => {
    const res = await apiClient.get('/reports/intake-discrepancies', { params: { format } })
    return res.data
  },
  validationFindings: async (severity?: string, format: 'json' | 'csv' = 'json') => {
    const res = await apiClient.get('/reports/validation-findings', { params: { severity, format } })
    return res.data
  },
  anomalies: async (syncAlerts = false) => {
    const res = await apiClient.get('/reports/anomalies', { params: { sync_alerts: syncAlerts } })
    return res.data
  },
  auditLogs: async (limit = 100, action?: string, format: 'json' | 'csv' = 'json') => {
    const res = await apiClient.get('/reports/audit-logs', { params: { limit, action, format } })
    return res.data
  },
  enrolmentSummaryCsvUrl: () => `${apiClient.defaults.baseURL}/reports/enrolment-summary?format=csv`,
  intakeDiscrepanciesCsvUrl: () => `${apiClient.defaults.baseURL}/reports/intake-discrepancies?format=csv`,
  validationFindingsCsvUrl: (sev?: string) => `${apiClient.defaults.baseURL}/reports/validation-findings?format=csv${sev ? `&severity=${sev}` : ''}`,
  auditLogsCsvUrl: () => `${apiClient.defaults.baseURL}/reports/audit-logs?format=csv`,
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const dashboardApi = {
  college: async (institution_id?: string): Promise<CollegeDashboard> => {
    const res = await apiClient.get('/dashboard/college', {
      params: institution_id ? { institution_id } : {},
    })
    return res.data
  },
  aicte: async (): Promise<AICTEDashboard> => {
    const res = await apiClient.get('/dashboard/aicte')
    return res.data
  },
  analytics: async (): Promise<any> => {
    const res = await apiClient.get('/dashboard/analytics')
    return res.data
  },
  dataQuality: async (institution_id?: string): Promise<any> => {
    const res = await apiClient.get('/dashboard/data-quality', {
      params: institution_id ? { institution_id } : {},
    })
    return res.data
  },
}
