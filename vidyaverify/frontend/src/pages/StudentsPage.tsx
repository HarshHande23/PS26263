import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { studentsApi } from '@/api'
import { Users, Search, Plus, ChevronRight, Eye } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

const STATUS_COLORS: Record<string, string> = {
  active: 'bg-green-100 text-green-700',
  inactive: 'bg-slate-100 text-slate-500',
  transferred: 'bg-blue-100 text-blue-700',
  graduated: 'bg-purple-100 text-purple-700',
  dropped: 'bg-red-100 text-red-600',
  suspended: 'bg-orange-100 text-orange-700',
}
const VALIDATION_COLORS: Record<string, string> = {
  open: 'bg-amber-100 text-amber-700',
  resolved: 'bg-green-100 text-green-700',
  dismissed: 'bg-slate-100 text-slate-500',
  under_review: 'bg-blue-100 text-blue-700',
}

export default function StudentsPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')
  const canCreate = ['super_admin', 'aicte_admin', 'college_admin', 'admission_staff'].includes(user?.role ?? '')

  const { data, isLoading, error } = useQuery({
    queryKey: ['students', page, search, statusFilter],
    queryFn: () => studentsApi.list({
      page, size: 20,
      search: search || undefined,
      enrolment_status: statusFilter || undefined,
    }),
    placeholderData: (prev) => prev,
  })

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Students</h1>
          <p className="text-slate-500 text-sm mt-1">Student enrolment records</p>
        </div>
        {canCreate && (
          <Link to="/students/new"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            <Plus size={16} /> Add Student
          </Link>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text" placeholder="Search by name or enrolment number…"
            value={search} onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="w-full pl-9 pr-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select
          value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          className="px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="graduated">Graduated</option>
          <option value="transferred">Transferred</option>
          <option value="dropped">Dropped</option>
          <option value="suspended">Suspended</option>
        </select>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-48 text-slate-400">Loading students…</div>
        ) : error ? (
          <div className="p-6 text-red-600">Failed to load students.</div>
        ) : !data?.items.length ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-400">
            <Users size={32} className="mb-2 opacity-30" />
            <p>No students found</p>
            {canCreate && (
              <Link to="/students/new" className="mt-3 text-blue-600 text-sm hover:underline">Add the first student</Link>
            )}
          </div>
        ) : (
          <>
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-5 py-3 text-slate-600 font-medium">Name</th>
                  <th className="text-left px-5 py-3 text-slate-600 font-medium hidden md:table-cell">Enrolment No.</th>
                  <th className="text-left px-5 py-3 text-slate-600 font-medium hidden lg:table-cell">APAAR</th>
                  <th className="text-left px-5 py-3 text-slate-600 font-medium">Enrolment</th>
                  <th className="text-left px-5 py-3 text-slate-600 font-medium hidden md:table-cell">Validation</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map(s => (
                  <tr key={s.id} className="hover:bg-slate-50">
                    <td className="px-5 py-3 font-medium text-slate-800">{s.full_name}</td>
                    <td className="px-5 py-3 hidden md:table-cell font-mono text-xs text-slate-600">{s.enrolment_number ?? '—'}</td>
                    <td className="px-5 py-3 hidden lg:table-cell font-mono text-xs text-slate-400">{s.apaar_id_masked ?? '—'}</td>
                    <td className="px-5 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[s.enrolment_status] ?? ''}`}>
                        {s.enrolment_status}
                      </span>
                    </td>
                    <td className="px-5 py-3 hidden md:table-cell">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${VALIDATION_COLORS[s.validation_status] ?? ''}`}>
                        {s.validation_status}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <Link to={`/students/${s.id}`}
                        className="flex items-center gap-1 text-blue-600 hover:text-blue-800 text-xs">
                        <Eye size={12} /> View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {data.pages > 1 && (
              <div className="flex items-center justify-between px-5 py-3 border-t border-slate-100 text-sm text-slate-500">
                <span>Page {page} of {data.pages} ({data.total} total)</span>
                <div className="flex gap-2">
                  <button onClick={() => setPage(p => p - 1)} disabled={page === 1}
                    className="px-3 py-1 border border-slate-200 rounded disabled:opacity-40 hover:bg-slate-50">Prev</button>
                  <button onClick={() => setPage(p => p + 1)} disabled={page >= data.pages}
                    className="px-3 py-1 border border-slate-200 rounded disabled:opacity-40 hover:bg-slate-50">Next</button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
