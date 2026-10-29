import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/api'
import { Building2, Users, AlertTriangle, Copy, Upload, Bell } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

function StatCard({ label, value, icon, color }: {
  label: string; value: number; icon: React.ReactNode; color: string
}) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
        {icon}
      </div>
      <div>
        <div className="text-2xl font-bold text-slate-800">{value.toLocaleString()}</div>
        <div className="text-sm text-slate-500">{label}</div>
      </div>
    </div>
  )
}

export default function AICTEDashboard() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard', 'aicte'],
    queryFn: dashboardApi.aicte,
  })

  if (isLoading) return (
    <div className="flex items-center justify-center h-64 text-slate-400">Loading AICTE dashboard…</div>
  )
  if (error) return (
    <div className="p-8 text-red-600">Failed to load dashboard data.</div>
  )

  const chartData = (stats?.institution_summary ?? []).map(inst => ({
    name: inst.short_name ?? inst.name.substring(0, 15),
    students: inst.active_students,
  }))

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">AICTE Administrator Dashboard</h1>
        <p className="text-slate-500 text-sm mt-1">Cross-institution overview of student data and compliance</p>
        <div className="mt-2 inline-flex items-center gap-2 px-3 py-1 bg-amber-50 border border-amber-200 rounded-full text-xs text-amber-700">
          ⚠️ All data is synthetic — not connected to real APAAR/AICTE systems
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Institutions" value={stats?.total_institutions ?? 0}
          icon={<Building2 size={22} className="text-blue-600" />} color="bg-blue-50" />
        <StatCard label="Total Students" value={stats?.total_students ?? 0}
          icon={<Users size={22} className="text-indigo-600" />} color="bg-indigo-50" />
        <StatCard label="Open Findings" value={stats?.open_findings ?? 0}
          icon={<AlertTriangle size={22} className="text-amber-600" />} color="bg-amber-50" />
        <StatCard label="Suspected Duplicates" value={stats?.suspected_duplicates ?? 0}
          icon={<Copy size={22} className="text-red-600" />} color="bg-red-50" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
          <div className="text-xl font-bold text-slate-800">{stats?.active_students?.toLocaleString() ?? 0}</div>
          <div className="text-sm text-slate-500 mt-1">Active Enrolments</div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
          <div className="text-xl font-bold text-slate-800">{stats?.total_submissions ?? 0}</div>
          <div className="text-sm text-slate-500 mt-1">Upload Submissions</div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
          <div className="text-xl font-bold text-amber-600">{stats?.open_alerts ?? 0}</div>
          <div className="text-sm text-slate-500 mt-1">Open Alerts</div>
        </div>
      </div>

      {/* Institution chart */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="font-semibold text-slate-700 mb-4">Active Students by Institution</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="students" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Institution summary table */}
      {stats?.institution_summary && stats.institution_summary.length > 0 && (
        <div className="mt-6 bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-5 py-3 border-b border-slate-100 font-semibold text-slate-700 text-sm">
            Institution Summary
          </div>
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left px-5 py-3 text-slate-600 font-medium">Institution</th>
                <th className="text-right px-5 py-3 text-slate-600 font-medium">Active Students</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {stats.institution_summary.map(inst => (
                <tr key={inst.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3 text-slate-800">{inst.name}</td>
                  <td className="px-5 py-3 text-right font-medium text-blue-700">{inst.active_students}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
