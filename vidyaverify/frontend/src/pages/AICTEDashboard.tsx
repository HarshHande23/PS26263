import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { dashboardApi, reportsApi } from '@/api'
import {
  Building2,
  Users,
  AlertTriangle,
  Copy,
  Upload,
  Bell,
  ShieldCheck,
  FileSpreadsheet,
  TrendingUp,
  Award,
  CheckCircle,
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
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
        <div className="text-2xl font-bold text-[#0B3C5D]">{typeof value === 'number' ? value.toLocaleString() : value}</div>
        <div className="text-xs text-gray-500 font-medium">{label}</div>
      </div>
    </div>
  )
}

const PIE_COLORS = ['#15803D', '#0B3C5D', '#D97706', '#DC2626', '#6B7280']

export default function AICTEDashboard() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard', 'aicte'],
    queryFn: dashboardApi.aicte,
  })

  const { data: analytics } = useQuery({
    queryKey: ['dashboard', 'analytics'],
    queryFn: dashboardApi.analytics,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
        <div className="w-8 h-8 border-4 border-[#0B3C5D] border-t-transparent rounded-full animate-spin mr-3" />
        Loading AICTE Central Dashboard...
      </div>
    )
  }

  if (error) {
    return <div className="p-8 text-red-600 bg-white rounded border border-red-200">Failed to load central dashboard data.</div>
  }

  const institutionChartData = (stats?.institution_summary ?? []).map((inst) => ({
    name: inst.short_name ?? inst.name.substring(0, 14),
    students: inst.active_students,
  }))

  const stateChartData = (analytics?.state_distribution ?? []).map((s: any) => ({
    state: s.state,
    count: s.count,
  }))

  const verificationPieData = analytics?.verification_breakdown
    ? Object.entries(analytics.verification_breakdown).map(([k, v]) => ({
        name: k.replace(/_/g, ' '),
        value: v as number,
      }))
    : []

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white p-6 rounded-lg border border-[#D6DCE4] shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-[#0B3C5D]" />
            <h1 className="text-2xl font-bold text-[#0B3C5D]">AICTE Central Regulatory Command</h1>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            National regulatory oversight of student admissions, approved intake capacities, and APAAR verification.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to="/reports"
            className="flex items-center gap-1.5 px-3 py-2 bg-[#0B3C5D] text-white rounded text-xs font-semibold hover:bg-[#072438] transition-colors shadow-sm"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" /> Compliance Reports &amp; CSV
          </Link>
          <Link
            to="/institutions"
            className="flex items-center gap-1.5 px-3 py-2 border border-gray-300 bg-white text-gray-700 rounded text-xs font-semibold hover:bg-gray-50 transition-colors shadow-sm"
          >
            <Building2 className="w-3.5 h-3.5 text-[#1D4E89]" /> Manage Institutions
          </Link>
        </div>
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Approved Institutions"
          value={stats?.total_institutions ?? 0}
          icon={<Building2 className="w-6 h-6 text-[#0B3C5D]" />}
        />
        <StatCard
          label="Total Registered Students"
          value={stats?.total_students ?? 0}
          icon={<Users className="w-6 h-6 text-[#1D4E89]" />}
        />
        <StatCard
          label="Open Validation Findings"
          value={stats?.open_findings ?? 0}
          icon={<AlertTriangle className="w-6 h-6 text-amber-600" />}
        />
        <StatCard
          label="Cross-Institution Duplicates"
          value={stats?.suspected_duplicates ?? 0}
          icon={<Copy className="w-6 h-6 text-rose-600" />}
        />
      </div>

      {/* National Capacity Metric Row */}
      {analytics && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg border border-[#D6DCE4] p-4 text-center">
            <span className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Total Approved Seats</span>
            <div className="text-xl font-bold text-[#0B3C5D] mt-1">{analytics.total_intake_capacity?.toLocaleString()}</div>
          </div>
          <div className="bg-white rounded-lg border border-[#D6DCE4] p-4 text-center">
            <span className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Overall Intake Utilization</span>
            <div className="text-xl font-bold text-emerald-700 mt-1">{analytics.overall_capacity_utilization}%</div>
          </div>
          <div className="bg-white rounded-lg border border-[#D6DCE4] p-4 text-center">
            <span className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Statistical Anomalies</span>
            <div className="text-xl font-bold text-amber-600 mt-1">{analytics.anomalies_detected} Flagged</div>
          </div>
        </div>
      )}

      {/* Analytical Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Students by Institution */}
        <div className="bg-white rounded-lg border border-[#D6DCE4] p-5 shadow-sm">
          <h2 className="font-bold text-sm text-[#0B3C5D] mb-4 pb-2 border-b uppercase tracking-wider">
            Active Student Enrolments by Institution
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={institutionChartData}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="students" fill="#0B3C5D" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* State-wise Distribution */}
        <div className="bg-white rounded-lg border border-[#D6DCE4] p-5 shadow-sm">
          <h2 className="font-bold text-sm text-[#0B3C5D] mb-4 pb-2 border-b uppercase tracking-wider">
            State-wise Student Distribution
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stateChartData}>
                <XAxis dataKey="state" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#1D4E89" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Institution Summary Table */}
      {stats?.institution_summary && stats.institution_summary.length > 0 && (
        <div className="bg-white rounded-lg border border-[#D6DCE4] shadow-sm overflow-hidden">
          <div className="px-5 py-3 border-b border-[#D6DCE4] bg-[#EEF5FA] font-bold text-[#0B3C5D] text-xs uppercase tracking-wider flex items-center justify-between">
            <span>Approved Institutions Registry Directory</span>
            <Link to="/institutions" className="text-xs text-[#1D4E89] lowercase font-normal hover:underline">
              view full directory &rarr;
            </Link>
          </div>
          <table className="w-full text-xs text-left">
            <thead className="bg-gray-50 border-b border-[#D6DCE4] text-gray-600 font-semibold">
              <tr>
                <th className="px-5 py-3">Institution Name</th>
                <th className="px-5 py-3">Short Name</th>
                <th className="px-5 py-3 text-right">Enrolled Active Students</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {stats.institution_summary.map((inst) => (
                <tr key={inst.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 font-semibold text-gray-800">{inst.name}</td>
                  <td className="px-5 py-3 text-gray-500 font-mono">{inst.short_name || '—'}</td>
                  <td className="px-5 py-3 text-right font-bold text-[#0B3C5D]">{inst.active_students}</td>
                  <td className="px-5 py-3 text-right">
                    <Link
                      to={`/institutions/${inst.id}`}
                      className="text-[#1D4E89] hover:underline font-semibold"
                    >
                      Dossier
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
