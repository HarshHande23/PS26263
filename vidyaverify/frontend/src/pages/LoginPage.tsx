import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Eye, EyeOff, AlertCircle, ShieldCheck, Lock, UserCheck } from 'lucide-react'
import { UtilityBar } from '@/components/gov/UtilityBar'
import { GovernmentFooter } from '@/components/gov/GovernmentFooter'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.')
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (demoEmail: string) => {
    setEmail(demoEmail)
    setPassword('Demo@1234')
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F6F8]">
      <UtilityBar />

      {/* Tricolour Accent */}
      <div className="h-1 w-full flex">
        <div className="w-1/3 bg-[#FF9933]" />
        <div className="w-1/3 bg-white border-y border-gray-200" />
        <div className="w-1/3 bg-[#138808]" />
      </div>

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-lg space-y-4 my-8">
          {/* Header */}
          <div className="text-center space-y-1">
            <div className="w-14 h-14 rounded-full border-2 border-[#0B3C5D] bg-[#EEF5FA] flex items-center justify-center font-serif font-black text-[#0B3C5D] text-xl mx-auto shadow-sm">
              AICTE
            </div>
            <h1 className="text-2xl font-bold text-[#0B3C5D] tracking-tight">
              विद्यावेरिफ़ाई <span className="font-semibold text-[#1D4E89]">| VidyaVerify</span>
            </h1>
            <p className="text-xs text-gray-600 font-medium">
              National APAAR-Based Student Data Management &amp; Regulatory Verification Portal
            </p>
          </div>

          {/* Login Card */}
          <div className="bg-white rounded-lg border border-[#D6DCE4] shadow-md overflow-hidden">
            <div className="bg-[#0B3C5D] text-white px-6 py-3 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-2">
                <Lock className="w-3.5 h-3.5" /> Institutional Single Sign-On
              </span>
              <span className="text-[10px] bg-[#1D4E89] text-gray-200 px-2 py-0.5 rounded font-mono">
                SECURE SSL/TLS
              </span>
            </div>

            <div className="p-6 space-y-4">
              {error && (
                <div className="flex items-center gap-2 p-3 rounded bg-red-50 border border-red-300 text-red-700 text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Official Email ID / Username
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="officer@aicte.gov.in or admin@institution.edu.in"
                    className="w-full px-3 py-2 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-[#0B3C5D] outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPw ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder="Enter authorized password"
                      className="w-full px-3 py-2 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-[#0B3C5D] outline-none pr-9"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPw(!showPw)}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 bg-[#0B3C5D] hover:bg-[#072438] disabled:opacity-50 text-white font-semibold rounded text-xs transition-colors shadow-sm"
                >
                  {loading ? 'Authenticating with Central Registry...' : 'Sign In to Portal'}
                </button>
              </form>

              {/* Security Warning Notice */}
              <div className="text-[11px] text-gray-500 bg-gray-50 p-2.5 rounded border border-gray-200">
                <strong>Statutory Notice:</strong> This portal is restricted to authorized institutional users and AICTE
                administrators. All access attempts and audit queries are logged with IP and cryptographic timestamps under the
                Information Technology Act.
              </div>

              {/* Demo Evaluation Accounts */}
              <div className="pt-2 border-t border-gray-200">
                <span className="text-[11px] font-bold text-gray-700 block mb-2 uppercase tracking-wide">
                  Quick Demo Evaluation Roles (Password: <code>Demo@1234</code>)
                </span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() => fillDemo('aicte.admin@aicte.gov.in')}
                    className="p-1.5 border border-gray-200 hover:bg-[#EEF5FA] hover:border-[#1D4E89] text-left rounded"
                  >
                    <div className="font-bold text-[#0B3C5D]">AICTE Admin</div>
                    <div className="text-[10px] text-gray-500 truncate">aicte.admin@aicte.gov.in</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => fillDemo('admin@coep.ac.in')}
                    className="p-1.5 border border-gray-200 hover:bg-[#EEF5FA] hover:border-[#1D4E89] text-left rounded"
                  >
                    <div className="font-bold text-[#0B3C5D]">College Admin</div>
                    <div className="text-[10px] text-gray-500 truncate">admin@coep.ac.in</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => fillDemo('staff@coep.ac.in')}
                    className="p-1.5 border border-gray-200 hover:bg-[#EEF5FA] hover:border-[#1D4E89] text-left rounded"
                  >
                    <div className="font-bold text-[#0B3C5D]">Admission Staff</div>
                    <div className="text-[10px] text-gray-500 truncate">staff@coep.ac.in</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => fillDemo('verifier@tcs.com')}
                    className="p-1.5 border border-gray-200 hover:bg-[#EEF5FA] hover:border-[#1D4E89] text-left rounded"
                  >
                    <div className="font-bold text-[#0B3C5D]">Authorized Verifier</div>
                    <div className="text-[10px] text-gray-500 truncate">verifier@tcs.com</div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <GovernmentFooter />
    </div>
  )
}
