import React from 'react'
import { LogOut, User as UserIcon, Shield, Building2 } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

export const GovernmentHeader: React.FC = () => {
  const { user, logout } = useAuth()

  const getRoleLabel = (role?: string) => {
    switch (role) {
      case 'super_admin':
        return 'Super Administrator'
      case 'aicte_admin':
        return 'AICTE Central Administrator'
      case 'college_admin':
        return 'College Administrator'
      case 'admission_staff':
        return 'Institutional Admission Staff'
      case 'authorized_verifier':
        return 'Authorized Verifier'
      case 'student':
        return 'Student Candidate'
      default:
        return 'Officer'
    }
  }

  return (
    <header className="bg-white border-b border-[#D6DCE4]">
      {/* Tricolour Accent Line */}
      <div className="h-1 w-full flex">
        <div className="w-1/3 bg-[#FF9933]" />
        <div className="w-1/3 bg-white border-y border-gray-200" />
        <div className="w-1/3 bg-[#138808]" />
      </div>

      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap justify-between items-center gap-4">
        {/* Emblem & Portal Identity */}
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-[#0B3C5D] bg-[#EEF5FA] flex items-center justify-center font-serif font-black text-[#0B3C5D] text-lg shadow-sm">
            AICTE
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl md:text-2xl font-bold text-[#0B3C5D] tracking-tight">
                विद्यावेरिफ़ाई <span className="font-semibold text-[#1D4E89]">| VidyaVerify</span>
              </h1>
              <span className="text-[11px] font-medium bg-[#EEF5FA] text-[#0B3C5D] px-2 py-0.5 rounded border border-[#D6DCE4]">
                v2.0 Official Prototype
              </span>
            </div>
            <p className="text-xs text-gray-600 font-medium">
              National APAAR-Based Student Data Management &amp; Regulatory Verification Platform
            </p>
          </div>
        </div>

        {/* User Card & Actions */}
        {user && (
          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <div className="text-xs font-semibold text-gray-800 flex items-center justify-end gap-1">
                <UserIcon className="w-3.5 h-3.5 text-[#1D4E89]" />
                {user.full_name}
              </div>
              <div className="text-[11px] text-gray-500 flex items-center justify-end gap-1 font-mono">
                <Shield className="w-3 h-3 text-[#0B3C5D]" />
                <span className="font-sans font-medium text-[#0B3C5D]">{getRoleLabel(user.role)}</span>
              </div>
            </div>

            <button
              onClick={logout}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-red-50 hover:text-red-700 border border-gray-300 transition-colors"
              title="Logout from VidyaVerify"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Logout</span>
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
