import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi } from '@/api'
import { useAuth } from '@/hooks/useAuth'
import {
  Bell,
  AlertTriangle,
  AlertCircle,
  CheckCircle,
  Clock,
  Filter,
  CheckSquare,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react'
import { StatusBadge } from '@/components/gov/StatusBadge'

export default function AlertsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [transitionDialog, setTransitionDialog] = useState<any>(null)
  const [targetStatus, setTargetStatus] = useState<string>('under_review')
  const [notes, setNotes] = useState<string>('')

  const instId = user?.role === 'college_admin' || user?.role === 'admission_staff' ? user.institution_id ?? undefined : undefined
  const isAicte = user?.role === 'super_admin' || user?.role === 'aicte_admin'

  const { data: alerts, isLoading, error } = useQuery({
    queryKey: ['alerts', instId, statusFilter, typeFilter],
    queryFn: () =>
      alertsApi.list({
        institution_id: instId,
        status: statusFilter || undefined,
        alert_type: typeFilter || undefined,
        limit: 100,
      }),
  })

  const transitionMutation = useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: string; notes?: string }) =>
      alertsApi.transition(id, status, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      setTransitionDialog(null)
      setNotes('')
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || 'Failed to update alert state')
    },
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg border border-[#D6DCE4] shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Bell className="w-6 h-6 text-[#0B3C5D]" />
            <h1 className="text-xl md:text-2xl font-bold text-[#0B3C5D]">
              Regulatory Alerts &amp; Discrepancy Workflows
            </h1>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Track, review, and remediate intake breaches, duplicate enrolments, and statistical anomalies.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-gray-400" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="border border-gray-300 rounded px-3 py-1.5 text-xs bg-white text-gray-700 outline-none"
          >
            <option value="">All Categories</option>
            <option value="ml_anomaly">ML Anomaly (Isolation Forest)</option>
            <option value="intake_exceeded">Intake Exceeded</option>
            <option value="cross_institution_duplicate">Cross-Institution Duplicate</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-gray-300 rounded px-3 py-1.5 text-xs bg-white text-gray-700 outline-none"
          >
            <option value="">All Lifecycle Stages</option>
            <option value="open">Open (Action Required)</option>
            <option value="under_review">Under Regulatory Review</option>
            <option value="awaiting_institution_correction">Awaiting College Correction</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
            <option value="dismissed">Dismissed</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-white rounded-lg border border-[#D6DCE4] shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-gray-400 text-xs">
            <div className="w-8 h-8 border-4 border-[#0B3C5D] border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading regulatory alerts...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-600 text-xs">Failed to load alerts.</div>
        ) : !alerts || alerts.length === 0 ? (
          <div className="p-12 text-center text-gray-500 flex flex-col items-center gap-2">
            <CheckCircle className="w-10 h-10 text-emerald-500" />
            <span className="font-bold text-gray-700 text-sm">No Active Alerts</span>
            <p className="text-xs text-gray-400">All intake numbers, validations, and verification metrics are within compliance bounds.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {alerts.map((alert) => (
              <div key={alert.id} className="p-5 hover:bg-gray-50 transition-colors">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <StatusBadge status={alert.severity} />
                      <span className="text-[11px] font-mono bg-gray-100 text-gray-700 px-2 py-0.5 rounded border border-gray-200">
                        {alert.alert_type}
                      </span>
                      {alert.anomaly_score !== null && alert.anomaly_score !== undefined && (
                        <span className="text-[11px] font-mono bg-purple-50 text-purple-700 font-semibold px-2 py-0.5 rounded border border-purple-200">
                          Score: {alert.anomaly_score.toFixed(4)}
                        </span>
                      )}
                      {alert.risk_level && (
                        <span className={`text-[11px] font-bold uppercase px-2 py-0.5 rounded border ${
                          alert.risk_level === 'critical' ? 'bg-red-50 text-red-700 border-red-200' :
                          alert.risk_level === 'high' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                          alert.risk_level === 'medium' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                          'bg-blue-50 text-blue-700 border-blue-200'
                        }`}>
                          Risk: {alert.risk_level}
                        </span>
                      )}
                      <span
                        className={`text-[11px] font-bold px-2 py-0.5 rounded uppercase ${
                          alert.status === 'open'
                            ? 'bg-amber-100 text-amber-900 border border-amber-300'
                            : alert.status === 'resolved'
                            ? 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                            : alert.status === 'under_review'
                            ? 'bg-blue-100 text-blue-900 border border-blue-300'
                            : 'bg-gray-100 text-gray-700 border border-gray-300'
                        }`}
                      >
                        {alert.status?.replace('_', ' ')}
                      </span>
                      <span className="text-[11px] text-gray-400 flex items-center gap-1 font-mono">
                        <Clock className="w-3 h-3" />
                        {new Date(alert.created_at).toLocaleString()}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-gray-900">{alert.title}</h3>
                    {alert.message && <p className="text-xs text-gray-600 leading-relaxed">{alert.message}</p>}

                    {alert.detected_issues && alert.detected_issues.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {alert.detected_issues.map((issue, idx) => (
                          <span key={idx} className="text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200 font-sans">
                            &bull; {issue}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => {
                        setTransitionDialog(alert)
                        setTargetStatus('under_review')
                        setNotes('')
                      }}
                      className="px-3 py-1.5 bg-[#0B3C5D] text-white rounded text-xs font-semibold hover:bg-[#072438] transition-colors shadow-sm flex items-center gap-1"
                    >
                      <span>Update Workflow State</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Transition Modal */}
      {transitionDialog && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full border border-gray-300 shadow-2xl p-6 space-y-4">
            <h3 className="text-sm font-bold text-[#0B3C5D] border-b pb-2">
              Update Alert Workflow State
            </h3>

            <div className="text-xs text-gray-600 bg-gray-50 p-3 rounded border border-gray-200">
              <span className="font-semibold text-gray-800">Alert:</span> {transitionDialog.title}
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-700">Target Lifecycle Status:</label>
              <select
                value={targetStatus}
                onChange={(e) => setTargetStatus(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-xs bg-white text-gray-800 outline-none"
              >
                {isAicte && <option value="under_review">Mark Under Regulatory Review</option>}
                {isAicte && <option value="awaiting_institution_correction">Request Institution Correction</option>}
                <option value="acknowledged">Acknowledge Alert</option>
                <option value="resolved">Mark as Resolved &amp; Remediated</option>
                {isAicte && <option value="dismissed">Dismiss Alert (False Positive)</option>}
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-700">Resolution / Review Notes:</label>
              <textarea
                rows={3}
                placeholder="Explain justification, correction proof, or regulatory directive..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full border border-gray-300 rounded p-2 text-xs outline-none focus:ring-1 focus:ring-[#0B3C5D]"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t">
              <button
                onClick={() => setTransitionDialog(null)}
                className="px-3 py-1.5 border border-gray-300 rounded text-xs text-gray-600 hover:bg-gray-50 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={() =>
                  transitionMutation.mutate({
                    id: transitionDialog.id,
                    status: targetStatus,
                    notes: notes || undefined,
                  })
                }
                disabled={transitionMutation.isPending}
                className="px-4 py-1.5 bg-[#0B3C5D] text-white rounded text-xs font-semibold hover:bg-[#072438] disabled:opacity-50"
              >
                {transitionMutation.isPending ? 'Updating...' : 'Confirm Transition'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
