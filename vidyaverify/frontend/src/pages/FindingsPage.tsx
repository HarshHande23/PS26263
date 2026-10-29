import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { findingsApi } from '@/api'
import { useAuth } from '@/hooks/useAuth'
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Filter,
  Users,
  ShieldCheck,
  Check,
  MessageSquare,
  ArrowRight,
} from 'lucide-react'
import { StatusBadge } from '@/components/gov/StatusBadge'

export default function FindingsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const isAicte = user?.role === 'super_admin' || user?.role === 'aicte_admin'

  const [severityFilter, setSeverityFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('open')
  const [activeTab, setActiveTab] = useState<'findings' | 'duplicates'>('findings')
  const [resolvingId, setResolvingId] = useState<string | null>(null)
  const [resolutionNote, setResolutionNote] = useState<string>('')

  // Duplicate review dialog
  const [dupDialog, setDupDialog] = useState<any>(null)
  const [dupStatus, setDupStatus] = useState<string>('under_review')
  const [dupNotes, setDupNotes] = useState<string>('')

  const instId =
    user?.role === 'college_admin' || user?.role === 'admission_staff' ? user.institution_id ?? undefined : undefined

  const { data: findingsData, isLoading: loadingFindings } = useQuery({
    queryKey: ['findings', instId, severityFilter, statusFilter],
    queryFn: () =>
      findingsApi.list({
        institution_id: instId,
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
        size: 50,
      }),
  })

  const { data: duplicates, isLoading: loadingDuplicates } = useQuery({
    queryKey: ['duplicates', instId],
    queryFn: () => findingsApi.duplicates({ institution_id: instId }),
    enabled: activeTab === 'duplicates',
  })

  const resolveMutation = useMutation({
    mutationFn: ({ id, note }: { id: string; note?: string }) => findingsApi.resolve(id, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['findings'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      setResolvingId(null)
      setResolutionNote('')
    },
  })

  const dismissMutation = useMutation({
    mutationFn: (id: string) => findingsApi.dismiss(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['findings'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })

  const reviewDupMutation = useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: string; notes?: string }) =>
      findingsApi.reviewDuplicate(id, status, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['duplicates'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      setDupDialog(null)
      setDupNotes('')
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || 'Failed to review duplicate case')
    },
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg border border-[#D6DCE4] shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-[#0B3C5D]" />
            <h1 className="text-xl md:text-2xl font-bold text-[#0B3C5D]">
              Data Quality Findings &amp; Duplicate Review Center
            </h1>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Track automated field-level validation errors, cross-institutional duplicate enrolments, and remediation notes.
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="flex bg-[#EEF5FA] p-1 rounded border border-[#D6DCE4]">
          <button
            onClick={() => setActiveTab('findings')}
            className={`px-4 py-1.5 text-xs font-semibold rounded transition-colors ${
              activeTab === 'findings' ? 'bg-[#0B3C5D] text-white shadow-sm' : 'text-gray-600 hover:text-black'
            }`}
          >
            Validation Findings
          </button>
          <button
            onClick={() => setActiveTab('duplicates')}
            className={`px-4 py-1.5 text-xs font-semibold rounded transition-colors ${
              activeTab === 'duplicates' ? 'bg-[#0B3C5D] text-white shadow-sm' : 'text-gray-600 hover:text-black'
            }`}
          >
            Duplicate Enrolment Cases
          </button>
        </div>
      </div>

      {activeTab === 'findings' ? (
        <div className="space-y-4">
          {/* Filters Bar */}
          <div className="bg-white p-4 rounded-lg border border-[#D6DCE4] shadow-sm flex flex-wrap items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5 text-gray-700 font-semibold">
              <Filter className="w-3.5 h-3.5 text-gray-500" /> Filter Findings:
            </div>
            <div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="border border-gray-300 rounded px-2.5 py-1 bg-white text-gray-700 outline-none"
              >
                <option value="">All Statuses</option>
                <option value="open">Open Findings</option>
                <option value="resolved">Resolved Findings</option>
                <option value="dismissed">Dismissed Findings</option>
              </select>
            </div>
            <div>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="border border-gray-300 rounded px-2.5 py-1 bg-white text-gray-700 outline-none"
              >
                <option value="">All Severities</option>
                <option value="error">Errors Only</option>
                <option value="warning">Warnings Only</option>
              </select>
            </div>
          </div>

          {/* Findings List */}
          <div className="bg-white rounded-lg border border-[#D6DCE4] shadow-sm overflow-hidden">
            {loadingFindings ? (
              <div className="p-12 text-center text-gray-400 text-xs">
                <div className="w-8 h-8 border-4 border-[#0B3C5D] border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                Scanning validation findings...
              </div>
            ) : !findingsData || findingsData.items.length === 0 ? (
              <div className="p-12 text-center text-gray-500 flex flex-col items-center gap-2">
                <CheckCircle2 className="w-10 h-10 text-emerald-500" />
                <span className="font-bold text-gray-800 text-sm">No Validation Discrepancies</span>
                <p className="text-xs text-gray-400">All student records comply with format and intake requirements.</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {findingsData.items.map((item) => (
                  <div key={item.id} className="p-5 hover:bg-gray-50 transition-colors">
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                      <div className="space-y-1.5 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <StatusBadge status={item.severity} />
                          <span className="text-[11px] font-mono bg-gray-100 px-2 py-0.5 rounded text-gray-700">
                            Rule: {item.rule_id}
                          </span>
                          <span
                            className={`text-[11px] font-bold px-2 py-0.5 rounded uppercase ${
                              item.status === 'open'
                                ? 'bg-amber-100 text-amber-900 border border-amber-300'
                                : 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                            }`}
                          >
                            {item.status}
                          </span>
                          <span className="text-[11px] text-gray-400 font-mono">
                            {new Date(item.created_at).toLocaleString()}
                          </span>
                        </div>

                        <h3 className="text-sm font-bold text-gray-900">{item.title}</h3>
                        {item.description && <p className="text-xs text-gray-600 leading-relaxed">{item.description}</p>}
                        {item.recommendation && (
                          <div className="text-xs text-[#0B3C5D] bg-[#EEF5FA] p-2 rounded border border-[#D6DCE4] mt-1 font-medium">
                            <strong>Recommended Action:</strong> {item.recommendation}
                          </div>
                        )}
                        {item.resolution_note && (
                          <div className="text-xs text-emerald-800 bg-emerald-50 p-2 rounded border border-emerald-200 mt-1">
                            <strong>Resolution Note:</strong> {item.resolution_note}
                          </div>
                        )}
                      </div>

                      {item.status === 'open' && (
                        <div className="shrink-0 flex items-center gap-2">
                          {resolvingId === item.id ? (
                            <div className="flex flex-col gap-2 p-3 bg-gray-50 border rounded text-xs w-64">
                              <input
                                type="text"
                                placeholder="Correction note (e.g. Updated DOB)..."
                                value={resolutionNote}
                                onChange={(e) => setResolutionNote(e.target.value)}
                                className="border p-1.5 rounded text-xs outline-none"
                              />
                              <div className="flex gap-2">
                                <button
                                  onClick={() =>
                                    resolveMutation.mutate({ id: item.id, note: resolutionNote || undefined })
                                  }
                                  className="px-2 py-1 bg-emerald-600 text-white rounded font-bold hover:bg-emerald-700"
                                >
                                  Confirm
                                </button>
                                <button
                                  onClick={() => setResolvingId(null)}
                                  className="px-2 py-1 border rounded hover:bg-gray-100"
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          ) : (
                            <>
                              <button
                                onClick={() => setResolvingId(item.id)}
                                className="px-3 py-1.5 bg-emerald-600 text-white rounded text-xs font-semibold hover:bg-emerald-700 shadow-sm"
                              >
                                Resolve
                              </button>
                              <button
                                onClick={() => dismissMutation.mutate(item.id)}
                                className="px-3 py-1.5 border border-gray-300 text-gray-700 rounded text-xs font-semibold hover:bg-gray-100 shadow-sm"
                              >
                                Dismiss
                              </button>
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Cross-Institution Duplicates Tab */
        <div className="space-y-4">
          <div className="bg-white rounded-lg border border-[#D6DCE4] shadow-sm overflow-hidden">
            <div className="p-5 border-b border-[#D6DCE4] bg-[#EEF5FA]">
              <h2 className="text-sm font-bold text-[#0B3C5D] flex items-center gap-2">
                <Users className="w-4 h-4 text-[#1D4E89]" />
                Multi-Institution Concurrent Enrolment Allegations
              </h2>
              <p className="text-xs text-gray-600 mt-1">
                Generated when matching APAAR IDs or exact name + DOB combinations are registered across multiple AICTE institutions.
              </p>
            </div>

            {loadingDuplicates ? (
              <div className="p-12 text-center text-gray-400 text-xs">
                <div className="w-8 h-8 border-4 border-[#0B3C5D] border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                Cross-referencing institutional databases...
              </div>
            ) : !duplicates || duplicates.length === 0 ? (
              <div className="p-12 text-center text-gray-500 flex flex-col items-center gap-2">
                <CheckCircle2 className="w-10 h-10 text-emerald-500" />
                <span className="font-bold text-gray-800 text-sm">No Cross-Institution Duplicates</span>
                <p className="text-xs text-gray-400">All registered candidates maintain single, distinct institutional affiliations.</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {duplicates.map((dup) => (
                  <div key={dup.id} className="p-5 hover:bg-gray-50 transition-colors">
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                      <div className="space-y-1.5 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="bg-red-100 text-red-900 border border-red-300 text-[11px] font-bold px-2 py-0.5 rounded uppercase">
                            Confidence: {dup.confidence}
                          </span>
                          <span
                            className={`text-[11px] font-bold px-2 py-0.5 rounded uppercase ${
                              dup.status === 'confirmed'
                                ? 'bg-red-200 text-red-900 border border-red-400'
                                : dup.status === 'dismissed'
                                ? 'bg-gray-100 text-gray-700 border border-gray-300'
                                : 'bg-amber-100 text-amber-900 border border-amber-300'
                            }`}
                          >
                            {dup.status}
                          </span>
                          <span className="text-[11px] text-gray-400 font-mono">Case: {dup.id}</span>
                        </div>

                        <h3 className="text-sm font-bold text-gray-900">{dup.match_reason}</h3>
                        <div className="text-xs text-gray-600 font-mono">
                          Candidate A ID: <code className="bg-gray-100 px-1 py-0.5 rounded">{dup.student_a_id}</code> &bull;
                          Candidate B ID: <code className="bg-gray-100 px-1 py-0.5 rounded">{dup.student_b_id}</code>
                        </div>
                        {dup.notes && (
                          <div className="text-xs text-gray-700 bg-gray-50 p-2 rounded border border-gray-200 mt-1">
                            <strong>Reviewer Notes:</strong> {dup.notes}
                          </div>
                        )}
                      </div>

                      {isAicte && (
                        <div className="shrink-0 flex items-center gap-2">
                          <button
                            onClick={() => {
                              setDupDialog(dup)
                              setDupStatus('under_review')
                              setDupNotes('')
                            }}
                            className="px-3 py-1.5 bg-[#0B3C5D] text-white rounded text-xs font-semibold hover:bg-[#072438] transition-colors shadow-sm flex items-center gap-1"
                          >
                            <span>Regulatory Adjudication</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Duplicate Review Dialog */}
      {dupDialog && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full border border-gray-300 shadow-2xl p-6 space-y-4">
            <h3 className="text-sm font-bold text-[#0B3C5D] border-b pb-2">
              Adjudicate Cross-Institution Duplicate Case
            </h3>

            <div className="text-xs text-gray-600 bg-gray-50 p-3 rounded border border-gray-200">
              <span className="font-semibold text-gray-800">Allegation:</span> {dupDialog.match_reason}
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-700">Adjudication Ruling:</label>
              <select
                value={dupStatus}
                onChange={(e) => setDupStatus(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-1.5 text-xs bg-white text-gray-800 outline-none"
              >
                <option value="under_review">Mark Under Investigation</option>
                <option value="confirmed">Confirm Fraudulent Duplicate Enrolment</option>
                <option value="dismissed">Dismiss Case (Legitimate Separate Identity)</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-700">Official Adjudication Finding Notes:</label>
              <textarea
                rows={3}
                placeholder="Detail verification documents examined and regulatory decision..."
                value={dupNotes}
                onChange={(e) => setDupNotes(e.target.value)}
                className="w-full border border-gray-300 rounded p-2 text-xs outline-none focus:ring-1 focus:ring-[#0B3C5D]"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t">
              <button
                onClick={() => setDupDialog(null)}
                className="px-3 py-1.5 border border-gray-300 rounded text-xs text-gray-600 hover:bg-gray-50 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={() =>
                  reviewDupMutation.mutate({
                    id: dupDialog.id,
                    status: dupStatus,
                    notes: dupNotes || undefined,
                  })
                }
                disabled={reviewDupMutation.isPending}
                className="px-4 py-1.5 bg-[#0B3C5D] text-white rounded text-xs font-semibold hover:bg-[#072438] disabled:opacity-50"
              >
                {reviewDupMutation.isPending ? 'Saving...' : 'Submit Ruling'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
