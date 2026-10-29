import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi } from '@/api'
import { useAuth } from '@/hooks/useAuth'
import { Bell, AlertTriangle, AlertCircle, CheckCircle, Check, Filter, Clock } from 'lucide-react'

export default function AlertsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<string>('open')

  const instId = user?.institution_id ?? undefined

  const { data: alerts, isLoading, error } = useQuery({
    queryKey: ['alerts', instId, statusFilter],
    queryFn: () => alertsApi.list({
      institution_id: instId,
      status: statusFilter || undefined,
      limit: 50,
    }),
  })

  const ackMutation = useMutation({
    mutationFn: (id: string) => alertsApi.acknowledge(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Bell className="text-amber-500" size={24} />
            Institutional Alerts & System Notifications
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Real-time warnings regarding intake overflow, duplicate enrolments, and integrity discrepancies.
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-2">
          <Filter size={16} className="text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">All Alerts</option>
            <option value="open">Open (Unacknowledged)</option>
            <option value="acknowledged">Acknowledged</option>
          </select>
        </div>
      </div>

      {/* Alerts list */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        {isLoading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading alerts...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-600 text-sm">Failed to load alerts.</div>
        ) : !alerts || alerts.length === 0 ? (
          <div className="p-12 text-center text-slate-500 flex flex-col items-center gap-2">
            <CheckCircle size={36} className="text-emerald-500" />
            <span className="font-semibold text-slate-700">No active alerts</span>
            <p className="text-xs text-slate-400">All intake numbers and enrolment metrics are operating within thresholds.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {alerts.map((alert) => (
              <div key={alert.id} className="p-5 hover:bg-slate-50/60 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg shrink-0 mt-0.5 ${
                      alert.severity === 'error'
                        ? 'bg-red-50 text-red-600'
                        : 'bg-amber-50 text-amber-600'
                    }`}>
                      {alert.severity === 'error' ? <AlertCircle size={20} /> : <AlertTriangle size={20} />}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${
                          alert.severity === 'error'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-amber-100 text-amber-700'
                        }`}>
                          {alert.severity}
                        </span>
                        <span className="text-xs font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-600">
                          {alert.alert_type}
                        </span>
                        <span className="text-xs text-slate-400 flex items-center gap-1">
                          <Clock size={12} />
                          {new Date(alert.created_at).toLocaleString()}
                        </span>
                      </div>
                      <h3 className="text-base font-semibold text-slate-900 mt-1">{alert.title}</h3>
                      {alert.message && (
                        <p className="text-sm text-slate-600 mt-1">{alert.message}</p>
                      )}
                    </div>
                  </div>

                  {alert.status === 'open' ? (
                    <button
                      onClick={() => ackMutation.mutate(alert.id)}
                      disabled={ackMutation.isPending}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 shrink-0 self-start sm:self-auto"
                    >
                      <Check size={14} />
                      Acknowledge
                    </button>
                  ) : (
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 shrink-0 self-start sm:self-auto">
                      Acknowledged
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
