import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { institutionsApi } from '@/api'
import { Building2, ArrowLeft, GraduationCap, Calendar, BookOpen } from 'lucide-react'

export default function InstitutionDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: inst, isLoading, error } = useQuery({
    queryKey: ['institution', id],
    queryFn: () => institutionsApi.get(id!),
    enabled: !!id,
  })
  const { data: programmes } = useQuery({
    queryKey: ['programmes', id],
    queryFn: () => institutionsApi.programmes(id!),
    enabled: !!id,
  })
  const { data: academicYears } = useQuery({
    queryKey: ['academic-years', id],
    queryFn: () => institutionsApi.academicYears(id!),
    enabled: !!id,
  })

  if (isLoading) return <div className="flex items-center justify-center h-64 text-slate-400">Loading…</div>
  if (error || !inst) return <div className="p-8 text-red-600">Institution not found.</div>

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <Link to="/institutions" className="flex items-center gap-1 text-slate-500 hover:text-slate-700 text-sm mb-6">
        <ArrowLeft size={14} /> Back to Institutions
      </Link>

      <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <Building2 size={28} className="text-blue-600" />
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-slate-800">{inst.name}</h1>
            {inst.short_name && <div className="text-sm text-slate-500">{inst.short_name}</div>}
            <div className="flex flex-wrap gap-2 mt-2">
              <span className="px-2 py-0.5 rounded-full text-xs bg-blue-100 text-blue-700 font-medium">
                {inst.aicte_id}
              </span>
              <span className="px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-600">
                {inst.institution_type.replace('_', ' ')}
              </span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                inst.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'
              }`}>
                {inst.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-5 border-t border-slate-100 text-sm">
          <div><div className="text-slate-400 text-xs mb-1">State</div><div className="font-medium">{inst.state}</div></div>
          <div><div className="text-slate-400 text-xs mb-1">City</div><div className="font-medium">{inst.city ?? '—'}</div></div>
          <div><div className="text-slate-400 text-xs mb-1">Established</div><div className="font-medium">{inst.establishment_year ?? '—'}</div></div>
          <div><div className="text-slate-400 text-xs mb-1">Email</div><div className="font-medium truncate">{inst.email ?? '—'}</div></div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Programmes */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen size={18} className="text-blue-500" />
            <h2 className="font-semibold text-slate-700">Programmes ({programmes?.length ?? 0})</h2>
          </div>
          {!programmes?.length ? (
            <p className="text-slate-400 text-sm">No programmes configured.</p>
          ) : (
            <ul className="space-y-2">
              {programmes.map(p => (
                <li key={p.id} className="flex items-center justify-between text-sm p-2 rounded-lg hover:bg-slate-50">
                  <span className="font-medium text-slate-700">{p.name}</span>
                  <span className="text-xs text-slate-400 font-mono">{p.code}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Academic Years */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Calendar size={18} className="text-blue-500" />
            <h2 className="font-semibold text-slate-700">Academic Years ({academicYears?.length ?? 0})</h2>
          </div>
          {!academicYears?.length ? (
            <p className="text-slate-400 text-sm">No academic years configured.</p>
          ) : (
            <ul className="space-y-2">
              {academicYears.map(ay => (
                <li key={ay.id} className="flex items-center justify-between text-sm p-2 rounded-lg hover:bg-slate-50">
                  <span className="font-medium text-slate-700">{ay.label}</span>
                  {ay.is_current && (
                    <span className="px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-700">Current</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
