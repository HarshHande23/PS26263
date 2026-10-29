import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { institutionsApi } from '@/api'
import { Building2, Search, ChevronRight, Plus } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

const TYPE_LABELS: Record<string, string> = {
  university: 'University',
  deemed_university: 'Deemed University',
  autonomous_college: 'Autonomous College',
  affiliated_college: 'Affiliated College',
  technical_institute: 'Technical Institute',
}

export default function InstitutionsPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const canCreate = ['super_admin', 'aicte_admin'].includes(user?.role ?? '')

  const { data, isLoading, error } = useQuery({
    queryKey: ['institutions', page, search],
    queryFn: () => institutionsApi.list({ page, size: 20, search: search || undefined }),
    placeholderData: (prev) => prev,
  })

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Institutions</h1>
          <p className="text-slate-500 text-sm mt-1">AICTE-approved institutions</p>
        </div>
        {canCreate && (
          <Link to="/institutions/new"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors">
            <Plus size={16} />
            Add Institution
          </Link>
        )}
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Search by name or AICTE ID…"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          className="w-full pl-9 pr-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-48 text-slate-400">Loading…</div>
        ) : error ? (
          <div className="p-6 text-red-600">Failed to load institutions.</div>
        ) : !data?.items.length ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-400">
            <Building2 size={32} className="mb-2 opacity-30" />
            <p>No institutions found</p>
          </div>
        ) : (
          <>
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-5 py-3 text-slate-600 font-medium">Institution</th>
                  <th className="text-left px-5 py-3 text-slate-600 font-medium hidden md:table-cell">AICTE ID</th>
                  <th className="text-left px-5 py-3 text-slate-600 font-medium hidden lg:table-cell">Type</th>
                  <th className="text-left px-5 py-3 text-slate-600 font-medium hidden lg:table-cell">State</th>
                  <th className="text-left px-5 py-3 text-slate-600 font-medium">Status</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map(inst => (
                  <tr key={inst.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3">
                      <div className="font-medium text-slate-800">{inst.name}</div>
                      {inst.short_name && <div className="text-xs text-slate-400">{inst.short_name}</div>}
                    </td>
                    <td className="px-5 py-3 hidden md:table-cell font-mono text-xs text-slate-600">{inst.aicte_id}</td>
                    <td className="px-5 py-3 hidden lg:table-cell text-slate-600">
                      {TYPE_LABELS[inst.institution_type] ?? inst.institution_type}
                    </td>
                    <td className="px-5 py-3 hidden lg:table-cell text-slate-600">{inst.state}</td>
                    <td className="px-5 py-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        inst.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'
                      }`}>
                        {inst.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <Link to={`/institutions/${inst.id}`}
                        className="text-blue-600 hover:text-blue-800 flex items-center gap-1 text-xs">
                        View <ChevronRight size={12} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            {data.pages > 1 && (
              <div className="flex items-center justify-between px-5 py-3 border-t border-slate-100 text-sm text-slate-500">
                <span>Showing {(page - 1) * 20 + 1}–{Math.min(page * 20, data.total)} of {data.total}</span>
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
