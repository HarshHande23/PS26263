import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { studentsApi } from '@/api'
import { ArrowLeft, Edit, Trash2, AlertTriangle, Clock } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

function Field({ label, value }: { label: string; value?: string | null | boolean }) {
  const display = typeof value === 'boolean' ? (value ? 'Yes' : 'No') : (value ?? '—')
  return (
    <div>
      <div className="text-xs text-slate-400 mb-0.5">{label}</div>
      <div className="text-sm font-medium text-slate-700">{String(display)}</div>
    </div>
  )
}

export default function StudentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const canEdit = ['super_admin', 'aicte_admin', 'college_admin', 'admission_staff'].includes(user?.role ?? '')
  const canDelete = ['super_admin', 'aicte_admin'].includes(user?.role ?? '')

  const { data: student, isLoading, error } = useQuery({
    queryKey: ['student', id],
    queryFn: () => studentsApi.get(id!),
    enabled: !!id,
  })
  const { data: history } = useQuery({
    queryKey: ['student-history', id],
    queryFn: () => studentsApi.history(id!),
    enabled: !!id,
  })

  const deleteMutation = useMutation({
    mutationFn: () => studentsApi.delete(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] })
      navigate('/students')
    },
  })

  if (isLoading) return <div className="flex items-center justify-center h-64 text-slate-400">Loading…</div>
  if (error || !student) return <div className="p-8 text-red-600">Student not found.</div>

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <Link to="/students" className="flex items-center gap-1 text-slate-500 hover:text-slate-700 text-sm mb-6">
        <ArrowLeft size={14} /> Back to Students
      </Link>

      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-slate-800">{student.full_name}</h1>
        <div className="flex gap-2">
          {canEdit && (
            <Link to={`/students/${id}/edit`}
              className="flex items-center gap-2 px-3 py-2 border border-slate-200 rounded-lg text-sm hover:bg-slate-50">
              <Edit size={14} /> Edit
            </Link>
          )}
          {canDelete && (
            <button
              onClick={() => confirm('Delete this student record?') && deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
              className="flex items-center gap-2 px-3 py-2 border border-red-200 text-red-600 rounded-lg text-sm hover:bg-red-50"
            >
              <Trash2 size={14} /> Delete
            </button>
          )}
        </div>
      </div>

      {/* Core Details */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 mb-4">
        <h2 className="font-semibold text-slate-700 mb-4">Core Information</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Field label="Enrolment Number" value={student.enrolment_number} />
          <Field label="APAAR ID (Masked)" value={student.apaar_id_masked} />
          <Field label="Date of Birth" value={student.date_of_birth} />
          <Field label="Gender" value={student.gender} />
          <Field label="Email" value={student.email} />
          <Field label="Phone" value={student.phone} />
          <Field label="Admission Date" value={student.admission_date} />
          <Field label="Admission Category" value={student.admission_category} />
        </div>
      </div>

      {/* Enrolment Details */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 mb-4">
        <h2 className="font-semibold text-slate-700 mb-4">Enrolment & Classification</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-xs text-slate-400 mb-0.5">Enrolment Status</div>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
              student.enrolment_status === 'active' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
            }`}>{student.enrolment_status}</span>
          </div>
          <div>
            <div className="text-xs text-slate-400 mb-0.5">Validation Status</div>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
              student.validation_status === 'open' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
            }`}>{student.validation_status}</span>
          </div>
          <Field label="Supernumerary" value={student.is_supernumerary} />
          <Field label="NRI" value={student.is_nri} />
          <Field label="OCI" value={student.is_oci} />
          <Field label="Foreign National" value={student.is_foreign_national} />
          <Field label="Person with Disability" value={student.is_pwd} />
        </div>
      </div>

      {/* Enrolment History */}
      {history && history.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Clock size={16} className="text-slate-400" />
            <h2 className="font-semibold text-slate-700">Enrolment History</h2>
          </div>
          <div className="space-y-3">
            {history.map((h: any) => (
              <div key={h.id} className="flex items-start gap-3 text-sm">
                <div className="w-2 h-2 mt-1.5 rounded-full bg-blue-400 flex-shrink-0" />
                <div>
                  <span className="font-medium">{h.status}</span>
                  {h.reason && <span className="text-slate-400 ml-2">— {h.reason}</span>}
                  <div className="text-xs text-slate-400">{new Date(h.created_at).toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
