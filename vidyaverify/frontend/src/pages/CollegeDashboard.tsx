import { useQuery } from '@tanstack/react-query'
import { dashboardApi, alertsApi } from '@/api'
import { useAuth } from '@/hooks/useAuth'
import { Users, AlertTriangle, Upload, AlertCircle, CheckCircle, Copy, Bell } from 'lucide-react'
import { Link } from 'react-router-dom'

function StatCard({ label, value, icon, color }: {
  label: string; value: number | string; icon: React.ReactNode; color: string
}) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
        {icon}
      </div>
      <div>
        <div className="text-2xl font-bold text-slate-800">{value}</div>
        <div className="text-sm text-slate-500">{label}</div>
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

  const { data: alerts } = useQuery({
    queryKey: ['alerts', 'open'],
    queryFn: () => alertsApi.list({ status: 'open', limit: 5 }),
  })

  if (isLoading) return (
    <div className="flex items-center justify-center h-64 text-slate-400">Loading dashboard…</div>
  )
  if (error) return (
    <div className="p-8 text-red-600">Failed to load dashboard data.</div>
  )

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">College Dashboard</h1>
        <p className="text-slate-500 text-sm mt-1">Overview of student records and validation status</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Total Students"
          value={stats?.total_students ?? 0}
          icon={<Users size={22} className="text-blue-600" />}
          color="bg-blue-50"
        />
        <StatCard
          label="Active Enrolments"
          value={stats?.active_students ?? 0}
          icon={<CheckCircle size={22} className="text-green-600" />}
          color="bg-green-50"
        />
        <StatCard
          label="Open Findings"
          value={stats?.open_findings ?? 0}
          icon={<AlertTriangle size={22} className="text-amber-600" />}
          color="bg-amber-50"
        />
        <StatCard
          label="Suspected Duplicates"
          value={stats?.suspected_duplicates ?? 0}
          icon={<Copy size={22} className="text-red-600" />}
          color="bg-red-50"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h2 className="font-semibold text-slate-700 mb-4">Quick Actions</h2>
          <div className="space-y-2">
            <Link to="/students/new"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 text-slate-700 text-sm transition-colors">
              <Users size={16} className="text-blue-500" />
              Add new student record
            </Link>
            <Link to="/upload"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 text-slate-700 text-sm transition-colors">
              <Upload size={16} className="text-blue-500" />
              Bulk import students (CSV/XLSX)
            </Link>
            <Link to="/findings?status=open"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 text-slate-700 text-sm transition-colors">
              <AlertTriangle size={16} className="text-amber-500" />
              Review open validation findings
            </Link>
            <Link to="/students"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 text-slate-700 text-sm transition-colors">
              <Users size={16} className="text-slate-400" />
              Browse student directory
            </Link>
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-700">Recent Alerts</h2>
            <Link to="/alerts" className="text-xs text-blue-600 hover:underline">View all</Link>
          </div>
          {!alerts || alerts.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-sm">
              <Bell size={24} className="mx-auto mb-2 opacity-40" />
              No open alerts
            </div>
          ) : (
            <div className="space-y-2">
              {alerts.slice(0, 5).map(alert => (
                <div key={alert.id} className="flex items-start gap-3 p-3 rounded-lg bg-amber-50 border border-amber-100">
                  <AlertCircle size={16} className="text-amber-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="text-sm font-medium text-slate-700">{alert.title}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{alert.alert_type}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Submission stats row */}
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
          <div className="text-xl font-bold text-slate-800">{stats?.total_submissions ?? 0}</div>
          <div className="text-sm text-slate-500 mt-1">Upload Submissions</div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
          <div className="text-xl font-bold text-red-600">{stats?.error_findings ?? 0}</div>
          <div className="text-sm text-slate-500 mt-1">Critical Errors</div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
          <div className="text-xl font-bold text-amber-600">{stats?.open_alerts ?? 0}</div>
          <div className="text-sm text-slate-500 mt-1">Open Alerts</div>
        </div>
      </div>
    </div>
  )
}
