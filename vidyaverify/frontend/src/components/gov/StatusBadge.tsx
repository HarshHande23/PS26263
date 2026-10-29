import React from 'react'
import { CheckCircle, AlertCircle, Clock, HelpCircle, XCircle } from 'lucide-react'

interface StatusBadgeProps {
  status?: string | null
  className?: string
  showSimulatedBadge?: boolean
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  className = '',
  showSimulatedBadge = true,
}) => {
  if (!status) return null

  const s = status.toUpperCase()

  // Verification Statuses
  if (s === 'VERIFIED_BY_PROVIDER' || s === 'VERIFIED') {
    return (
      <div className="inline-flex flex-wrap items-center gap-1.5">
        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300 ${className}`}>
          <CheckCircle className="w-3 h-3 text-emerald-600" />
          Verified
        </span>
        {showSimulatedBadge && (
          <span className="text-[10px] font-mono uppercase bg-blue-50 text-blue-700 px-1.5 py-0.2 rounded border border-blue-200">
            SIMULATED
          </span>
        )}
      </div>
    )
  }

  if (s === 'PENDING_EXTERNAL_VERIFICATION' || s === 'PENDING') {
    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-300 ${className}`}>
        <Clock className="w-3 h-3 text-amber-600" />
        Pending Verification
      </span>
    )
  }

  if (s === 'FORMAT_VALID') {
    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-sky-50 text-sky-800 border border-sky-300 ${className}`}>
        <CheckCircle className="w-3 h-3 text-sky-600" />
        Format Validated
      </span>
    )
  }

  if (s === 'NOT_VERIFIED' || s === 'ERROR' || s === 'FAILED') {
    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-300 ${className}`}>
        <XCircle className="w-3 h-3 text-rose-600" />
        Verification Failed
      </span>
    )
  }

  if (s === 'MANUAL_REVIEW_REQUIRED' || s === 'UNDER_REVIEW') {
    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-orange-50 text-orange-800 border border-orange-300 ${className}`}>
        <AlertCircle className="w-3 h-3 text-orange-600" />
        Manual Review Required
      </span>
    )
  }

  if (s === 'PROVIDER_UNAVAILABLE') {
    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-gray-100 text-gray-800 border border-gray-300 ${className}`}>
        <HelpCircle className="w-3 h-3 text-gray-600" />
        Provider Offline
      </span>
    )
  }

  if (s === 'NOT_CHECKED') {
    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-medium bg-gray-50 text-gray-600 border border-gray-200 ${className}`}>
        Unchecked
      </span>
    )
  }

  // Severity Badges
  if (s === 'CRITICAL') {
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-red-100 text-red-900 border border-red-400 ${className}`}>
        <AlertCircle className="w-3 h-3 text-red-700" />
        CRITICAL
      </span>
    )
  }
  if (s === 'HIGH') {
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-900 border border-amber-400 ${className}`}>
        HIGH
      </span>
    )
  }
  if (s === 'WARNING' || s === 'MEDIUM') {
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-yellow-50 text-yellow-800 border border-yellow-300 ${className}`}>
        WARNING
      </span>
    )
  }

  // Generic fallback
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200 ${className}`}>
      {status}
    </span>
  )
}
