import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { dashboardApi, alertsApi } from '@/api'
import { useAuth } from '@/hooks/useAuth'
import {
  Users,
  AlertTriangle,
  Upload,
  AlertCircle,
  CheckCircle,
  Copy,
  Bell,
  Award,
  ShieldCheck,
  TrendingUp,
  FileSpreadsheet,
  ArrowRight,
} from 'lucide-react'
import { Link } from 'react-router-dom'

function StatCard({
  label,
  value,
  icon,
}: {
  label: string
  value: number | string
  icon: React.ReactNode
}) {
  return (
    <div className="bg-white rounded-lg border border-[#D6DCE4] p-5 shadow-sm flex items-center gap-4">
      <div className="w-12 h-12 rounded bg-[#EEF5FA] border border-[#D6DCE4] flex items-center justify-center shrink-0">
        {icon}
      </div>
      <div>
        <div className="text-2xl font-bold text-[#0B3C5D]">{value}</div>
        <div className="text-xs text-gray-500 font-medium">{label}</div>
      </div>
    </div>
  )
}

export default function CollegeDashboard() {
  const { user } = useAuth()
  const instId = user?.institution_id ?? undefined

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard', 'college', instId],
    queryFn: () => dashboardApi.college(instId ?? undefined),
  })

  const { data: dqScore } = useQuery({
    queryKey: ['dashboard', 'data-quality', instId],
    queryFn: () => dashboardApi.dataQuality(instId ?? undefined),
  })

  const { data: alerts } = useQuery({
    queryKey: ['alerts', 'open', instId],
    queryFn: () => alertsApi.list({ institution_id: instId, status: 'open', limit: 5 }),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
        <div className="w-8 h-8 border-4 border-[#0B3C5D] border-t-transparent rounded-full animate-spin mr-3" />
        Loading institutional dashboard...
      </div>
    )
  }

  if (error) {
    return <div className="p-8 text-red-600 bg-white rounded border border-red-200">Failed to load institutional dashboard data.</div>
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white p-6 rounded-lg border border-[#D6DCE4] shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#0B3C5D]">Institutional Enrolment Dashboard</h1>
          <p className="text-xs text-gray-500 mt-1">
            Real-time monitoring of APAAR data completeness, verification readiness, and intake compliance.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to="/upload"
            className="flex items-center gap-1.5 px-3 py-2 bg-[#0B3C5D] text-white rounded text-xs font-semibold hover:bg-[#072438] transition-colors shadow-sm"
          >
            <Upload className="w-3.5 h-3.5" /> Bulk Import Enrolments
          </Link>
          <Link
            to="/reports"
            className="flex items-center gap-1.5 px-3 py-2 border border-gray-300 bg-white text-gray-700 rounded text-xs font-semibold hover:bg-gray-50 transition-colors shadow-sm"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-[#1D4E89]" /> Compliance Reports
          </Link>
        </div>
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Student Enrolments"
          value={stats?.total_students ?? 0}
          icon={<Users className="w-6 h-6 text-[#0B3C5D]" />}
        />
        <StatCard
          label="Active Candidates"
          value={stats?.active_students ?? 0}
          icon={<CheckCircle className="w-6 h-6 text-emerald-600" />}
        />
        <StatCard
          label="Open Validation Findings"
          value={stats?.open_findings ?? 0}
          icon={<AlertTriangle className="w-6 h-6 text-amber-600" />}
        />
        <StatCard
          label="Suspected Duplicate Cases"
          value={stats?.suspected_duplicates ?? 0}
          icon={<Copy className="w-6 h-6 text-rose-600" />}
        />
      </div>

      {/* Institutional Data Quality Score Section */}
      {dqScore && (
        <div className="bg-white rounded-lg border border-[#D6DCE4] p-6 shadow-sm space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-100 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-emerald-50 border border-emerald-300 flex items-center justify-center">
                <Award className="w-7 h-7 text-emerald-700" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-bold text-gray-900">Institutional Data Quality Index (IDQI)</h2>
                  <span className="bg-emerald-100 text-emerald-900 text-xs font-bold px-2.5 py-0.5 rounded border border-emerald-300 font-mono">
                    Grade {dqScore.grade} ({dqScore.overall_score}/100)
                  </span>
                </div>
                <p className="text-xs text-gray-500">
                  Calculated against national AICTE standards across completeness, APAAR allocation, and intake validity.
                </p>
              </div>
            </div>

            <Link
              to="/findings"
              className="text-xs font-semibold text-[#1D4E89] hover:underline flex items-center gap-1"
            >
              Resolve Findings <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
            <div className="bg-gray-50 p-3 rounded border border-gray-200">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-500 font-medium">Record Completeness</span>
                <span className="font-bold text-gray-800">{dqScore.completeness_score}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-[#0B3C5D] h-2 rounded-full"
                  style={{ width: `${Math.min(100, dqScore.completeness_score)}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-50 p-3 rounded border border-gray-200">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-500 font-medium">APAAR Coverage</span>
                <span className="font-bold text-gray-800">{dqScore.apaar_coverage_score}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-[#1D4E89] h-2 rounded-full"
                  style={{ width: `${Math.min(100, dqScore.apaar_coverage_score)}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-50 p-3 rounded border border-gray-200">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-500 font-medium">Format Validation</span>
                <span className="font-bold text-gray-800">{dqScore.format_validity_score}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-emerald-600 h-2 rounded-full"
                  style={{ width: `${Math.min(100, dqScore.format_validity_score)}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-50 p-3 rounded border border-gray-200">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-500 font-medium">Intake Compliance</span>
                <span className="font-bold text-gray-800">{dqScore.intake_compliance_score}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-amber-600 h-2 rounded-full"
                  style={{ width: `${Math.min(100, dqScore.intake_compliance_score)}%` }}
                />
              </div>
            </div>
          </div>

          {dqScore.recommendations && dqScore.recommendations.length > 0 && (
            <div className="bg-[#EEF5FA] p-3 rounded border border-[#D6DCE4] text-xs text-gray-700">
              <span className="font-bold text-[#0B3C5D]">Actionable Quality Improvement Directives:</span>
              <ul className="list-disc ml-5 mt-1 space-y-0.5 text-gray-600">
                {dqScore.recommendations.map((rec: string, idx: number) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Split Section: Quick Actions & Recent Regulatory Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white rounded-lg border border-[#D6DCE4] p-5 shadow-sm space-y-3">
          <h2 className="font-bold text-sm text-[#0B3C5D] border-b pb-2 uppercase tracking-wider">
            Operational Shortcuts
          </h2>
          <div className="space-y-2">
            <Link
              to="/students/new"
              className="flex items-center justify-between p-3 rounded border border-gray-200 hover:bg-gray-50 text-xs font-semibold text-gray-800 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-[#0B3C5D]" />
                <span>Register Single Student Candidate</span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-gray-400" />
            </Link>

            <Link
              to="/upload"
              className="flex items-center justify-between p-3 rounded border border-gray-200 hover:bg-gray-50 text-xs font-semibold text-gray-800 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Upload className="w-4 h-4 text-[#0B3C5D]" />
                <span>Bulk Import via AICTE Official Template (CSV/XLSX)</span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-gray-400" />
            </Link>

            <Link
              to="/findings?status=open"
              className="flex items-center justify-between p-3 rounded border border-gray-200 hover:bg-gray-50 text-xs font-semibold text-gray-800 transition-colors"
            >
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>Review Open Data Validation Warnings ({stats?.open_findings ?? 0})</span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-gray-400" />
            </Link>

            <Link
              to="/reports"
              className="flex items-center justify-between p-3 rounded border border-gray-200 hover:bg-gray-50 text-xs font-semibold text-gray-800 transition-colors"
            >
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="w-4 h-4 text-[#1D4E89]" />
                <span>Export Official AICTE Enrolment CSV Report</span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-gray-400" />
            </Link>
          </div>
        </div>

        {/* Recent Regulatory Alerts */}
        <div className="bg-white rounded-lg border border-[#D6DCE4] p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b pb-2">
            <h2 className="font-bold text-sm text-[#0B3C5D] uppercase tracking-wider">
              Pending Regulatory Alerts
            </h2>
            <Link to="/alerts" className="text-xs text-[#1D4E89] font-semibold hover:underline">
              View All Alerts
            </Link>
          </div>

          {!alerts || alerts.length === 0 ? (
            <div className="text-center py-8 text-gray-400 text-xs">
              <CheckCircle className="w-8 h-8 mx-auto mb-2 text-emerald-500 opacity-60" />
              No unacknowledged alerts. Institution is compliant.
            </div>
          ) : (
            <div className="space-y-2">
              {alerts.slice(0, 4).map((alert) => (
                <div
                  key={alert.id}
                  className="p-3 rounded border border-amber-200 bg-amber-50/60 flex items-start justify-between gap-2"
                >
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                    <div>
                      <div className="text-xs font-bold text-gray-800">{alert.title}</div>
                      <div className="text-[11px] text-gray-500 font-mono mt-0.5">{alert.alert_type}</div>
                    </div>
                  </div>
                  <Link
                    to="/alerts"
                    className="text-[11px] font-semibold text-[#0B3C5D] hover:underline shrink-0"
                  >
                    Action
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
