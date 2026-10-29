import React, { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { studentsApi, verificationApi } from '@/api'
import {
  ArrowLeft,
  Edit,
  Trash2,
  Clock,
  ShieldCheck,
  QrCode,
  ExternalLink,
  Copy,
  Check,
  AlertTriangle,
  RefreshCw,
} from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { StatusBadge } from '@/components/gov/StatusBadge'

function Field({ label, value }: { label: string; value?: string | null | boolean }) {
  const display = typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value ?? '—'
  return (
    <div>
      <div className="text-xs text-gray-500 mb-0.5">{label}</div>
      <div className="text-sm font-semibold text-gray-800">{String(display)}</div>
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

  const [verifyMode, setVerifyMode] = useState<string>('')
  const [verifyLoading, setVerifyLoading] = useState<boolean>(false)
  const [verifyResult, setVerifyResult] = useState<any>(null)
  const [qrModal, setQrModal] = useState<any>(null)
  const [copied, setCopied] = useState<boolean>(false)

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

  const { data: verificationHistory } = useQuery({
    queryKey: ['verification-history', id],
    queryFn: () => verificationApi.history(id!),
    enabled: !!id,
  })

  const deleteMutation = useMutation({
    mutationFn: () => studentsApi.delete(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] })
      navigate('/students')
    },
  })

  const handleVerify = async () => {
    if (!id) return
    setVerifyLoading(true)
    setVerifyResult(null)
    try {
      const outcome = verifyMode ? verifyMode : undefined
      const res = await verificationApi.verifyStudent(id, outcome)
      setVerifyResult(res)
      queryClient.invalidateQueries({ queryKey: ['student', id] })
      queryClient.invalidateQueries({ queryKey: ['verification-history', id] })
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Verification error occurred')
    } finally {
      setVerifyLoading(false)
    }
  }

  const handleGenerateQr = async () => {
    if (!id) return
    try {
      const res = await verificationApi.generateQr(id)
      setQrModal(res)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to generate QR token')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 text-sm">
        <div className="w-8 h-8 border-4 border-[#0B3C5D] border-t-transparent rounded-full animate-spin mr-3" />
        Loading student dossier...
      </div>
    )
  }

  if (error || !student) {
    return <div className="p-8 text-red-600 bg-white rounded border border-red-200">Student not found.</div>
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <Link
        to="/students"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#1D4E89] hover:underline"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Student Registry
      </Link>

      {/* Top Header Card */}
      <div className="bg-white p-6 rounded-lg border border-[#D6DCE4] shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-[#0B3C5D]">{student.full_name}</h1>
            <StatusBadge status={student.verification_status || 'NOT_CHECKED'} />
          </div>
          <p className="text-xs text-gray-500 mt-1 font-mono">
            Enrolment No: {student.enrolment_number || 'N/A'} &bull; Masked APAAR: {student.apaar_id_masked || 'Not Assigned'}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleGenerateQr}
            className="flex items-center gap-1.5 px-3 py-2 bg-emerald-700 text-white rounded text-xs font-semibold hover:bg-emerald-800 transition-colors shadow-sm"
          >
            <QrCode className="w-3.5 h-3.5" /> Generate QR Token
          </button>

          {canEdit && (
            <Link
              to={`/students/${id}/edit`}
              className="flex items-center gap-1.5 px-3 py-2 border border-gray-300 rounded text-xs font-semibold text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
            >
              <Edit className="w-3.5 h-3.5" /> Edit Record
            </Link>
          )}

          {canDelete && (
            <button
              onClick={() => confirm('Are you sure you want to delete this student record?') && deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
              className="flex items-center gap-1.5 px-3 py-2 border border-red-300 text-red-700 rounded text-xs font-semibold hover:bg-red-50 transition-colors shadow-sm"
            >
              <Trash2 className="w-3.5 h-3.5" /> Delete
            </button>
          )}
        </div>
      </div>

      {/* APAAR Verification Action Panel */}
      <div className="bg-[#EEF5FA] border border-[#0B3C5D]/30 p-5 rounded-lg shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-[#0B3C5D]" />
            <div>
              <h3 className="text-sm font-bold text-[#0B3C5D]">Mock APAAR Verification Provider Adapter</h3>
              <p className="text-[11px] text-gray-600">
                Simulate verification request to APAAR mock service. Results are strictly labelled SIMULATED VERIFICATION.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={verifyMode}
              onChange={(e) => setVerifyMode(e.target.value)}
              className="text-xs border border-gray-300 rounded px-2.5 py-1.5 bg-white text-gray-700 outline-none"
            >
              <option value="">Simulation Mode: Standard Live Match</option>
              <option value="NOT_FOUND">Force: Identifier Not Found</option>
              <option value="MANUAL_REVIEW">Force: Manual Review Required</option>
              <option value="UNAVAILABLE">Force: Provider Unavailable</option>
              <option value="TIMEOUT">Force: Request Timeout</option>
            </select>

            <button
              onClick={handleVerify}
              disabled={verifyLoading}
              className="flex items-center gap-1.5 px-4 py-1.5 bg-[#0B3C5D] text-white rounded text-xs font-semibold hover:bg-[#072438] transition-colors disabled:opacity-50"
            >
              {verifyLoading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Verifying...
                </>
              ) : (
                'Run APAAR Verification'
              )}
            </button>
          </div>
        </div>

        {verifyResult && (
          <div className="bg-white p-4 rounded border border-[#D6DCE4] space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-gray-800">
                Status: <span className="font-mono text-[#0B3C5D]">{verifyResult.status}</span>
              </span>
              <span className="bg-blue-100 text-blue-900 text-[10px] font-bold px-2 py-0.5 rounded font-mono">
                {verifyResult.simulation_label}
              </span>
            </div>
            <p className="text-gray-700">{verifyResult.provider_message}</p>
            <p className="text-amber-800 text-[11px] bg-amber-50 p-2 rounded border border-amber-200">
              {verifyResult.disclaimer}
            </p>
          </div>
        )}
      </div>

      {/* QR Modal Dialog */}
      {qrModal && (
        <div className="bg-emerald-50 border border-emerald-300 p-5 rounded-lg space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-emerald-900 flex items-center gap-2">
              <QrCode className="w-4 h-4 text-emerald-700" />
              Cryptographic QR Verification Token Generated
            </h3>
            <button onClick={() => setQrModal(null)} className="text-xs text-gray-500 hover:text-black">
              Close
            </button>
          </div>

          <p className="text-xs text-emerald-800">
            This token can be scanned by employers or external verifiers to validate the student's authentic enrolment
            without revealing sensitive PII or unmasked APAAR IDs. Valid until:{' '}
            <strong>{new Date(qrModal.expires_at).toLocaleString()}</strong>.
          </p>

          <div className="flex items-center gap-2 bg-white p-2 rounded border border-emerald-200 text-xs">
            <span className="font-mono text-gray-600 truncate flex-1">
              {window.location.origin}/verify/{qrModal.qr_token}
            </span>
            <button
              onClick={() => {
                navigator.clipboard.writeText(`${window.location.origin}/verify/${qrModal.qr_token}`)
                setCopied(true)
                setTimeout(() => setCopied(false), 2000)
              }}
              className="px-2.5 py-1 bg-emerald-600 text-white rounded hover:bg-emerald-700 text-xs flex items-center gap-1 font-semibold"
            >
              {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied' : 'Copy'}
            </button>
            <a
              href={`/verify/${qrModal.qr_token}`}
              target="_blank"
              rel="noreferrer"
              className="px-2.5 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-xs flex items-center gap-1 font-semibold"
            >
              <ExternalLink className="w-3.5 h-3.5" /> Open
            </a>
          </div>
        </div>
      )}

      {/* Core Details Grid */}
      <div className="bg-white rounded-lg border border-[#D6DCE4] p-6 shadow-sm">
        <h2 className="font-bold text-sm text-[#0B3C5D] mb-4 pb-2 border-b border-gray-100 uppercase tracking-wider">
          Student Profile &amp; Identity
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <Field label="Enrolment Number" value={student.enrolment_number} />
          <Field label="Masked APAAR ID" value={student.apaar_id_masked} />
          <Field label="Date of Birth" value={student.date_of_birth} />
          <Field label="Gender" value={student.gender} />
          <Field label="Email Address" value={student.email} />
          <Field label="Mobile Phone" value={student.phone} />
          <Field label="Admission Date" value={student.admission_date} />
          <Field label="Admission Category" value={student.admission_category} />
        </div>
      </div>

      {/* Enrolment & Classification */}
      <div className="bg-white rounded-lg border border-[#D6DCE4] p-6 shadow-sm">
        <h2 className="font-bold text-sm text-[#0B3C5D] mb-4 pb-2 border-b border-gray-100 uppercase tracking-wider">
          Enrolment &amp; Regulatory Classification
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <div className="text-xs text-gray-500 mb-0.5">Enrolment Status</div>
            <span
              className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase ${
                student.enrolment_status === 'active'
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              {student.enrolment_status}
            </span>
          </div>

          <div>
            <div className="text-xs text-gray-500 mb-0.5">Validation Quality</div>
            <span
              className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase ${
                student.validation_status === 'resolved'
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-amber-100 text-amber-800'
              }`}
            >
              {student.validation_status}
            </span>
          </div>

          <Field label="Supernumerary Quota" value={student.is_supernumerary} />
          <Field label="NRI Quota" value={student.is_nri} />
          <Field label="OCI Candidate" value={student.is_oci} />
          <Field label="Foreign National" value={student.is_foreign_national} />
          <Field label="Person with Disability (PwD)" value={student.is_pwd} />
        </div>
      </div>

      {/* Verification History Logs */}
      {verificationHistory && verificationHistory.length > 0 && (
        <div className="bg-white rounded-lg border border-[#D6DCE4] p-6 shadow-sm">
          <h2 className="font-bold text-sm text-[#0B3C5D] mb-4 pb-2 border-b border-gray-100 uppercase tracking-wider flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#1D4E89]" />
            APAAR Verification Request History
          </h2>
          <div className="divide-y divide-gray-100">
            {verificationHistory.map((v: any) => (
              <div key={v.id} className="py-3 flex items-center justify-between text-xs">
                <div>
                  <div className="font-semibold text-gray-800 flex items-center gap-2">
                    <span>{v.status}</span>
                    <span className="font-mono text-[10px] text-gray-400">Ref: {v.request_reference}</span>
                  </div>
                  <div className="text-gray-500 text-[11px] mt-0.5">{v.response_message}</div>
                </div>
                <div className="text-right text-gray-400 font-mono text-[11px]">
                  {new Date(v.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Enrolment History */}
      {history && history.length > 0 && (
        <div className="bg-white rounded-lg border border-[#D6DCE4] p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4 pb-2 border-b border-gray-100">
            <Clock className="w-4 h-4 text-gray-400" />
            <h2 className="font-bold text-sm text-[#0B3C5D] uppercase tracking-wider">Enrolment Audit Log</h2>
          </div>
          <div className="space-y-3">
            {history.map((h: any) => (
              <div key={h.id} className="flex items-start gap-3 text-xs">
                <div className="w-2 h-2 mt-1 rounded-full bg-[#1D4E89] shrink-0" />
                <div>
                  <span className="font-semibold text-gray-800">{h.status}</span>
                  {h.reason && <span className="text-gray-500 ml-2">&bull; {h.reason}</span>}
                  <div className="text-gray-400 text-[11px] font-mono">{new Date(h.created_at).toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
