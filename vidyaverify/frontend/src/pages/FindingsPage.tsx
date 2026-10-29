import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { findingsApi } from '@/api'
import { useAuth } from '@/hooks/useAuth'
import {
  AlertTriangle, ShieldAlert, CheckCircle2, XCircle, Search,
  Filter, Check, Eye, HelpCircle, Layers, Users
} from 'lucide-react'

export default function FindingsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [severityFilter, setSeverityFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('open')
  const [activeTab, setActiveTab] = useState<'findings' | 'duplicates'>('findings')
  const [resolvingId, setResolvingId] = useState<string | null>(null)
  const [resolutionNote, setResolutionNote] = useState<string>('')

  const instId = user?.institution_id ?? undefined

  const { data: findingsData, isLoading: loadingFindings } = useQuery({
    queryKey: ['findings', instId, severityFilter, statusFilter],
    queryFn: () => findingsApi.list({
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

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Data Validation & Findings Engine</h1>
          <p className="text-slate-500 text-sm mt-1">
            Review automated validation discrepancies, duplicate enrolments, and regulatory intake flags.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex bg-slate-100 p-1 rounded-lg self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('findings')}
            className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-colors ${
              activeTab === 'findings'
                ? 'bg-white text-slate-800 shadow-sm'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Validation Findings
          </button>
          <button
            onClick={() => setActiveTab('duplicates')}
            className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-colors ${
              activeTab === 'duplicates'
                ? 'bg-white text-slate-800 shadow-sm'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Cross-Institution Duplicates
          </button>
        </div>
      </div>

      {activeTab === 'findings' ? (
        <div className="space-y-4">
          {/* Filters Bar */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-slate-600 font-medium">
              <Filter size={16} /> Filters:
            </div>
            <div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="under_review">Under Review</option>
                <option value="resolved">Resolved</option>
                <option value="dismissed">Dismissed</option>
              </select>
            </div>
            <div>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="">All Severities</option>
                <option value="error">Error (High)</option>
                <option value="warning">Warning (Medium)</option>
                <option value="info">Info (Low)</option>
              </select>
            </div>
          </div>

          {/* Findings List */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
            {loadingFindings ? (
              <div className="p-8 text-center text-slate-400 text-sm">Loading validation findings...</div>
            ) : !findingsData || findingsData.items.length === 0 ? (
              <div className="p-12 text-center text-slate-500 flex flex-col items-center gap-2">
                <CheckCircle2 size={36} className="text-emerald-500" />
                <span className="font-semibold text-slate-700">No findings match your criteria</span>
                <p className="text-xs text-slate-400">All scanned student records conform to validation rules.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {findingsData.items.map((item) => (
                  <div key={item.id} className="p-5 hover:bg-slate-50/60 transition-colors">
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                      <div className="space-y-1.5 max-w-3xl">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${
                            item.severity === 'error'
                              ? 'bg-red-100 text-red-700'
                              : item.severity === 'warning'
                              ? 'bg-amber-100 text-amber-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}>
                            {item.severity}
                          </span>
                          <span className="text-xs font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-600">
                            {item.rule_id}
                          </span>
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            item.status === 'open'
                              ? 'bg-rose-50 text-rose-700 border border-rose-200'
                              : item.status === 'resolved'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : 'bg-slate-100 text-slate-600'
                          }`}>
                            {item.status}
                          </span>
                        </div>

                        <h3 className="text-base font-semibold text-slate-900">{item.title}</h3>
                        {item.description && (
                          <p className="text-sm text-slate-600">{item.description}</p>
                        )}
                        {item.recommendation && (
                          <p className="text-xs text-slate-500 italic">
                            <span className="font-medium text-slate-600">Recommended Action:</span> {item.recommendation}
                          </p>
                        )}
                        {item.resolution_note && (
                          <p className="text-xs text-emerald-700 bg-emerald-50/70 p-2 rounded border border-emerald-100 mt-2">
                            <span className="font-semibold">Resolution Note:</span> {item.resolution_note}
                          </p>
                        )}
                      </div>

                      {/* Action buttons */}
                      {item.status === 'open' && (
                        <div className="flex items-center gap-2 shrink-0">
                          {resolvingId === item.id ? (
                            <div className="flex flex-col gap-2 p-2 bg-slate-50 rounded-lg border border-slate-200">
                              <input
                                type="text"
                                placeholder="Enter resolution note..."
                                value={resolutionNote}
                                onChange={(e) => setResolutionNote(e.target.value)}
                                className="px-2.5 py-1 text-xs border rounded bg-white"
                              />
                              <div className="flex gap-2">
                                <button
                                  onClick={() => resolveMutation.mutate({ id: item.id, note: resolutionNote })}
                                  disabled={resolveMutation.isPending}
                                  className="px-2.5 py-1 text-xs bg-emerald-600 text-white rounded hover:bg-emerald-700"
                                >
                                  Submit
                                </button>
                                <button
                                  onClick={() => setResolvingId(null)}
                                  className="px-2.5 py-1 text-xs bg-slate-200 text-slate-700 rounded hover:bg-slate-300"
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          ) : (
                            <>
                              <button
                                onClick={() => setResolvingId(item.id)}
                                className="px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100"
                              >
                                Resolve
                              </button>
                              <button
                                onClick={() => dismissMutation.mutate(item.id)}
                                disabled={dismissMutation.isPending}
                                className="px-3 py-1.5 text-xs font-medium text-slate-600 bg-slate-100 border border-slate-200 rounded-lg hover:bg-slate-200"
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
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="p-5 border-b border-slate-100">
            <h2 className="text-base font-semibold text-slate-800 flex items-center gap-2">
              <Users size={18} className="text-red-500" />
              Suspected Multi-Institution Enrolment Cases
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Automated review alerts generated when matching identifiers or names + DOB appear across institutions.
            </p>
          </div>

          {loadingDuplicates ? (
            <div className="p-8 text-center text-slate-400 text-sm">Searching cross-institution cases...</div>
          ) : !duplicates || duplicates.length === 0 ? (
            <div className="p-12 text-center text-slate-500 flex flex-col items-center gap-2">
              <CheckCircle2 size={36} className="text-emerald-500" />
              <span className="font-semibold text-slate-700">No duplicate cases identified</span>
              <p className="text-xs text-slate-400">All registered students have distinct institutional enrolments.</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {duplicates.map((dup) => (
                <div key={dup.id} className="p-5 hover:bg-slate-50/60">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-red-100 text-red-800 text-xs font-bold">
                          Confidence: {dup.confidence}
                        </span>
                        <span className="text-xs text-slate-500">Case ID: {dup.id}</span>
                      </div>
                      <div className="text-sm font-semibold text-slate-800 mt-1">
                        Match Reason: {dup.match_reason}
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">
                        Involves Student A: <code className="bg-slate-100 px-1 py-0.5 rounded">{dup.student_a_id}</code> and Student B: <code className="bg-slate-100 px-1 py-0.5 rounded">{dup.student_b_id}</code>
                      </div>
                    </div>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200">
                      {dup.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
