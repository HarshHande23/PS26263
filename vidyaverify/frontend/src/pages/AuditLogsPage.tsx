import React, { useState, useEffect } from 'react'
import { History, Download, Filter, Search, ShieldCheck, Loader2 } from 'lucide-react'
import { reportsApi } from '@/api'

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [downloading, setDownloading] = useState<boolean>(false)
  const [actionFilter, setActionFilter] = useState<string>('')
  const [limit, setLimit] = useState<number>(100)

  const fetchLogs = () => {
    setLoading(true)
    reportsApi
      .auditLogs(limit, actionFilter || undefined, 'json')
      .then((res) => {
        setLogs(res.data || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  const handleExportAuditLogs = async () => {
    setDownloading(true)
    try {
      const blob = await reportsApi.downloadAuditLogsCsv(actionFilter || undefined, limit)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `aicte_audit_logs_${new Date().toISOString().slice(0, 10)}.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Blob export failed, falling back to direct link:', err)
      window.open(reportsApi.auditLogsCsvUrl(), '_blank')
    } finally {
      setDownloading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
  }, [limit])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg border border-[#D6DCE4] shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <History className="w-6 h-6 text-[#0B3C5D]" />
            <h1 className="text-xl md:text-2xl font-bold text-[#0B3C5D]">System Audit Trail &amp; Chain of Custody</h1>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Immutable regulatory audit log of administrative actions, bulk imports, validations, and verification queries.
          </p>
        </div>

        <button
          onClick={handleExportAuditLogs}
          disabled={downloading}
          className="flex items-center gap-1.5 px-3 py-2 bg-[#0B3C5D] text-white rounded text-xs font-semibold hover:bg-[#072438] active:scale-95 transition-all shadow-sm disabled:opacity-50 cursor-pointer"
        >
          {downloading ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Download className="w-3.5 h-3.5" />
          )}
          Export Audit Log CSV
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-lg border border-[#D6DCE4] shadow-sm flex flex-wrap items-center gap-4 text-xs">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Filter by action keyword (e.g. 'student', 'upload', 'verify')..."
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchLogs()}
            className="w-full border border-gray-300 rounded px-3 py-1.5 text-xs focus:ring-1 focus:ring-[#0B3C5D] outline-none"
          />
          <button
            onClick={fetchLogs}
            className="px-3 py-1.5 bg-[#1D4E89] text-white rounded font-semibold hover:bg-[#0B3C5D]"
          >
            Filter
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-gray-500 font-medium">Log entries:</span>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="border border-gray-300 rounded px-2 py-1 text-xs outline-none"
          >
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={250}>250</option>
            <option value={500}>500</option>
          </select>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-lg border border-[#D6DCE4] shadow-sm overflow-hidden">
        {loading ? (
          <div className="py-12 text-center text-gray-500 text-sm">
            <div className="w-8 h-8 border-4 border-[#0B3C5D] border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading system audit logs...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-[#EEF5FA] border-b border-[#D6DCE4] text-[#0B3C5D] font-bold">
                  <th className="p-3">Timestamp (UTC)</th>
                  <th className="p-3">Action</th>
                  <th className="p-3">Actor (User ID)</th>
                  <th className="p-3">Resource Type</th>
                  <th className="p-3">Resource ID</th>
                  <th className="p-3">IP Address</th>
                  <th className="p-3">Context Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 font-mono">
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="p-8 text-center text-gray-500 font-sans">
                      No audit log entries matching your criteria.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="p-3 text-gray-500 whitespace-nowrap">
                        {log.created_at ? new Date(log.created_at).toLocaleString() : 'N/A'}
                      </td>
                      <td className="p-3 font-bold text-[#0B3C5D] font-sans">{log.action}</td>
                      <td className="p-3 text-gray-600 truncate max-w-[120px]">{log.user_id}</td>
                      <td className="p-3 font-sans text-gray-700">{log.resource_type || '—'}</td>
                      <td className="p-3 text-gray-500 truncate max-w-[120px]">{log.resource_id || '—'}</td>
                      <td className="p-3 text-gray-500">{log.ip_address || '127.0.0.1'}</td>
                      <td className="p-3 text-gray-700 font-sans text-[11px] max-w-xs truncate" title={log.details}>
                        {log.details || '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

