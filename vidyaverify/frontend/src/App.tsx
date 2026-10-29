import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/hooks/useAuth'
import AppLayout from '@/layouts/AppLayout'
import LoginPage from '@/pages/LoginPage'
import CollegeDashboard from '@/pages/CollegeDashboard'
import AICTEDashboard from '@/pages/AICTEDashboard'
import InstitutionsPage from '@/pages/InstitutionsPage'
import InstitutionDetailPage from '@/pages/InstitutionDetailPage'
import StudentsPage from '@/pages/StudentsPage'
import StudentDetailPage from '@/pages/StudentDetailPage'
import StudentFormPage from '@/pages/StudentFormPage'
import UploadPage from '@/pages/UploadPage'
import SubmissionDetailPage from '@/pages/SubmissionDetailPage'
import FindingsPage from '@/pages/FindingsPage'
import AlertsPage from '@/pages/AlertsPage'
import { ReportsPage } from '@/pages/ReportsPage'
import { AuditLogsPage } from '@/pages/AuditLogsPage'
import { QRVerifyPublicPage } from '@/pages/QRVerifyPublicPage'
import type { UserRole } from '@/types'

function ProtectedRoute({
  children,
  allowedRoles,
}: {
  children: React.ReactNode
  allowedRoles?: UserRole[]
}) {
  const { user, isLoading } = useAuth()
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen text-gray-500 text-sm">
        <div className="w-8 h-8 border-4 border-[#0B3C5D] border-t-transparent rounded-full animate-spin mr-3" />
        Validating session credentials...
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-2 p-4 text-center">
        <h2 className="text-xl font-bold text-red-600">Access Restricted</h2>
        <p className="text-gray-500 text-sm">You do not possess the required regulatory authorization for this view.</p>
      </div>
    )
  }
  return <>{children}</>
}

function DashboardRedirect() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (['super_admin', 'aicte_admin'].includes(user.role)) {
    return <Navigate to="/dashboard/aicte" replace />
  }
  return <Navigate to="/dashboard/college" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Verification Route (QR Scanning / Certificate Check) */}
          <Route path="/verify/:token" element={<QRVerifyPublicPage />} />

          {/* Authentication */}
          <Route path="/login" element={<LoginPage />} />

          {/* Authenticated Government Portal Shell */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardRedirect />} />
            <Route path="dashboard/college" element={<CollegeDashboard />} />
            <Route
              path="dashboard/aicte"
              element={
                <ProtectedRoute allowedRoles={['super_admin', 'aicte_admin']}>
                  <AICTEDashboard />
                </ProtectedRoute>
              }
            />
            <Route path="institutions" element={<InstitutionsPage />} />
            <Route path="institutions/:id" element={<InstitutionDetailPage />} />
            <Route path="students" element={<StudentsPage />} />
            <Route path="students/new" element={<StudentFormPage />} />
            <Route path="students/:id" element={<StudentDetailPage />} />
            <Route path="students/:id/edit" element={<StudentFormPage />} />
            <Route path="upload" element={<UploadPage />} />
            <Route path="upload/:id" element={<SubmissionDetailPage />} />
            <Route path="findings" element={<FindingsPage />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route
              path="audit-logs"
              element={
                <ProtectedRoute allowedRoles={['super_admin', 'aicte_admin']}>
                  <AuditLogsPage />
                </ProtectedRoute>
              }
            />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
