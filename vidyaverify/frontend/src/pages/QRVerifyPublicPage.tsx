import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { CheckCircle2, XCircle, AlertTriangle, ShieldCheck, Building2, Calendar, FileText, ArrowLeft } from 'lucide-react'
import { verificationApi } from '@/api'
import { UtilityBar } from '@/components/gov/UtilityBar'
import { GovernmentFooter } from '@/components/gov/GovernmentFooter'

export const QRVerifyPublicPage: React.FC = () => {
  const { token } = useParams<{ token: string }>()
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    if (!token) {
      setError('Verification token is missing')
      setLoading(false)
      return
    }

    verificationApi
      .publicVerifyToken(token)
      .then((res) => {
        setData(res)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Failed to verify token or token has expired')
        setLoading(false)
      })
  }, [token])

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F6F8]">
      <UtilityBar />

      {/* Header */}
      <div className="bg-white border-b border-[#D6DCE4] py-4 px-4 shadow-sm">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full border-2 border-[#0B3C5D] bg-[#EEF5FA] flex items-center justify-center font-serif font-black text-[#0B3C5D] text-sm">
              AICTE
            </div>
            <div>
              <h1 className="text-lg font-bold text-[#0B3C5D]">
                VidyaVerify Public Verification Portal
              </h1>
              <p className="text-xs text-gray-500">Official Candidate Enrolment &amp; Credential Validation</p>
            </div>
          </div>
          <Link
            to="/login"
            className="text-xs font-semibold text-[#1D4E89] hover:underline flex items-center gap-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Institutional Login
          </Link>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 max-w-3xl w-full mx-auto px-4 py-8">
        {loading && (
          <div className="bg-white p-10 rounded-lg border border-[#D6DCE4] shadow-sm text-center">
            <div className="w-10 h-10 border-4 border-[#0B3C5D] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-sm font-semibold text-gray-700">Validating cryptographic QR token against registry...</p>
          </div>
        )}

        {error && (
          <div className="bg-white p-8 rounded-lg border border-red-200 shadow-sm text-center">
            <XCircle className="w-14 h-14 text-red-600 mx-auto mb-3" />
            <h2 className="text-xl font-bold text-red-900 mb-2">Token Verification Failed</h2>
            <p className="text-sm text-gray-600 mb-6">{error}</p>
            <div className="bg-red-50 p-4 rounded text-xs text-red-800 text-left border border-red-200">
              <strong>Possible causes:</strong>
              <ul className="list-disc ml-5 mt-1 space-y-1">
                <li>The QR token has exceeded its 7-day cryptographic validity window.</li>
                <li>The token was revoked following student enrolment cancellation.</li>
                <li>The verification token URL has been truncated or corrupted.</li>
              </ul>
            </div>
          </div>
        )}

        {data && (
          <div className="bg-white rounded-lg border border-[#D6DCE4] shadow-md overflow-hidden">
            {/* Top Verification Status Banner */}
            <div className="bg-[#15803D] text-white p-6 text-center">
              <ShieldCheck className="w-16 h-16 mx-auto mb-2 text-white" />
              <h2 className="text-2xl font-bold tracking-tight">Authentic Enrolment Record Verified</h2>
              <p className="text-xs text-green-100 mt-1">
                Cryptographically authenticated against institution registry records
              </p>
            </div>

            {/* Mandatory Simulated Verification Disclaimer */}
            <div className="bg-blue-50 border-b border-blue-200 px-6 py-3 text-xs text-blue-900 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-blue-700 shrink-0" />
              <span>
                <strong>SIMULATED VERIFICATION NOTICE:</strong> {data.disclaimer}
              </span>
            </div>

            {/* Candidate Details */}
            <div className="p-6 space-y-6">
              <div className="border-b border-gray-200 pb-4">
                <span className="text-[11px] uppercase tracking-wider text-gray-500 font-semibold">Candidate Name</span>
                <h3 className="text-xl font-bold text-gray-900">{data.full_name}</h3>
                <span className="text-xs text-gray-500 font-mono">Enrolment No: {data.enrolment_number}</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-3 rounded border border-gray-200">
                  <span className="text-[11px] text-gray-500 font-medium flex items-center gap-1">
                    <Building2 className="w-3.5 h-3.5 text-[#0B3C5D]" /> Approved Institution
                  </span>
                  <p className="text-sm font-semibold text-gray-800 mt-1">{data.institution_name}</p>
                </div>

                <div className="bg-gray-50 p-3 rounded border border-gray-200">
                  <span className="text-[11px] text-gray-500 font-medium flex items-center gap-1">
                    <FileText className="w-3.5 h-3.5 text-[#0B3C5D]" /> Enrolled Programme
                  </span>
                  <p className="text-sm font-semibold text-gray-800 mt-1">{data.programme_name}</p>
                </div>

                <div className="bg-gray-50 p-3 rounded border border-gray-200">
                  <span className="text-[11px] text-gray-500 font-medium flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-[#0B3C5D]" /> Academic Cohort
                  </span>
                  <p className="text-sm font-semibold text-gray-800 mt-1">{data.academic_year}</p>
                </div>

                <div className="bg-gray-50 p-3 rounded border border-gray-200">
                  <span className="text-[11px] text-gray-500 font-medium flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Verification Mode
                  </span>
                  <p className="text-sm font-semibold text-emerald-800 mt-1">
                    {data.verification_status} (SIMULATED)
                  </p>
                </div>
              </div>

              {/* Cryptographic Metadata */}
              <div className="bg-gray-50 p-4 rounded text-xs text-gray-600 border border-gray-200 space-y-1">
                <div className="flex justify-between">
                  <span>Certificate Issued At:</span>
                  <span className="font-mono text-gray-800">
                    {data.issued_at ? new Date(data.issued_at).toLocaleString() : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Cryptographic Token Expiration:</span>
                  <span className="font-mono text-gray-800">
                    {data.expires_at ? new Date(data.expires_at).toLocaleString() : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Registry Validation Status:</span>
                  <span className="font-semibold text-emerald-700">RECORD ACTIVE &amp; AUTHENTICATED</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <GovernmentFooter />
    </div>
  )
}
