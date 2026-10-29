import React, { useState, useEffect } from 'react'
import {
  FileSpreadsheet,
  Download,
  AlertOctagon,
  RefreshCw,
  Building,
  CheckCircle,
  FileText,
  ShieldAlert,
  Loader2,
} from 'lucide-react'
import { reportsApi } from '@/api'
import { useAuth } from '@/hooks/useAuth'

export const ReportsPage: React.FC = () => {
  const { user } = useAuth()
  const isAicte = user?.role === 'super_admin' || user?.role === 'aicte_admin'

  const [activeTab, setActiveTab] = useState<'enrolment' | 'discrepancies' | 'anomalies' | 'findings'>(
    'enrolment'
  )
  const [loading, setLoading] = useState<boolean>(false)
  const [downloading, setDownloading] = useState<boolean>(false)
  const [reportData, setReportData] = useState<any[]>([])
  const [anomalyData, setAnomalyData] = useState<any[]>([])
  const [syncNotice, setSyncNotice] = useState<string | null>(null)

  const handleExport = async (type: 'enrolment' | 'discrepancies' | 'findings') => {
    setDownloading(true)
    try {
      let blob: Blob
      let filename = ''
      if (type === 'enrolment') {
        blob = await reportsApi.downloadEnrolmentCsv()
        filename = `aicte_enrolment_summary_${new Date().toISOString().slice(0, 10)}.csv`
      } else if (type === 'discrepancies') {
        blob = await reportsApi.downloadDiscrepanciesCsv()
        filename = `aicte_intake_discrepancies_${new Date().toISOString().slice(0, 10)}.csv`
      } else {
        blob = await reportsApi.downloadFindingsCsv()
        filename = `aicte_validation_findings_${new Date().toISOString().slice(0, 10)}.csv`
      }
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Blob export failed, falling back to direct URL:', err)
      let fallbackUrl = ''
      if (type === 'enrolment') fallbackUrl = reportsApi.enrolmentSummaryCsvUrl()
      else if (type === 'discrepancies') fallbackUrl = reportsApi.intakeDiscrepanciesCsvUrl()
      else fallbackUrl = reportsApi.validationFindingsCsvUrl()
      window.open(fallbackUrl, '_blank')
    } finally {
      setDownloading(false)
    }
  }

  const loadCurrentReport = () => {
    setLoading(true)
    setSyncNotice(null)

    if (activeTab === 'enrolment') {
      reportsApi
        .enrolmentSummary('json')
        .then((res) => {
          setReportData(res.data || [])
          setLoading(false)
        })
        .catch(() => setLoading(false))
    } else if (activeTab === 'discrepancies') {
      reportsApi
        .intakeDiscrepancies('json')
        .then((res) => {
          setReportData(res.data || [])
          setLoading(false)
        })
        .catch(() => setLoading(false))
    } else if (activeTab === 'anomalies') {
      reportsApi
        .anomalies(false)
        .then((res) => {
          setAnomalyData(res.anomalies || [])
          setLoading(false)
        })
        .catch(() => setLoading(false))
    } else if (activeTab === 'findings') {
      reportsApi
        .validationFindings(undefined, 'json')
        .then((res) => {
          setReportData(res.data || [])
          setLoading(false)
        })
        .catch(() => setLoading(false))
    }
  }

  useEffect(() => {
    loadCurrentReport()
  }, [activeTab])

  const triggerAnomalySync = async () => {
    setLoading(true)
    try {
      const res = await reportsApi.anomalies(true)
      setAnomalyData(res.anomalies || [])
      setSyncNotice(`Anomaly scan completed! ${res.synced_to_alerts} new regulatory alerts synced to Alert Center.`)
      setLoading(false)
    } catch {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white p-6 rounded-lg border border-[#D6DCE4] shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-6 h-6 text-[#0B3C5D]" />
            <h1 className="text-xl md:text-2xl font-bold text-[#0B3C5D]">
              Regulatory Compliance &amp; Audit Reports
            </h1>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Export official government reports, intake utilization metrics, and explainable anomaly analyses.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {activeTab === 'enrolment' && (
            <button
              onClick={() => handleExport('enrolment')}
              disabled={downloading}
              className="flex items-center gap-1.5 px-3 py-2 bg-[#0B3C5D] text-white rounded text-xs font-semibold hover:bg-[#072438] active:scale-95 transition-all shadow-sm disabled:opacity-50 cursor-pointer"
            >
              {downloading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              Export Enrolment CSV
            </button>
          )}
          {activeTab === 'discrepancies' && isAicte && (
            <button
              onClick={() => handleExport('discrepancies')}
              disabled={downloading}
              className="flex items-center gap-1.5 px-3 py-2 bg-red-700 text-white rounded text-xs font-semibold hover:bg-red-800 active:scale-95 transition-all shadow-sm disabled:opacity-50 cursor-pointer"
            >
              {downloading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              Export Discrepancy CSV
            </button>
          )}
          {activeTab === 'findings' && (
            <button
              onClick={() => handleExport('findings')}
              disabled={downloading}
              className="flex items-center gap-1.5 px-3 py-2 bg-[#1D4E89] text-white rounded text-xs font-semibold hover:bg-[#0B3C5D] active:scale-95 transition-all shadow-sm disabled:opacity-50 cursor-pointer"
            >
              {downloading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              Export Findings CSV
            </button>
          )}
          {activeTab === 'anomalies' && isAicte && (
            <button
              onClick={triggerAnomalySync}
              className="flex items-center gap-1.5 px-3 py-2 bg-amber-600 text-white rounded text-xs font-semibold hover:bg-amber-700 transition-colors shadow-sm"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Run Scan &amp; Sync Alerts
            </button>
          )}
        </div>
      </div>

      {syncNotice && (
        <div className="bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs px-4 py-3 rounded flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{syncNotice}</span>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-[#D6DCE4] bg-white rounded-t px-2 pt-2 gap-1 overflow-x-auto">
        <button
          onClick={() => setActiveTab('enrolment')}
          className={`px-4 py-2 text-xs md:text-sm font-semibold border-b-2 whitespace-nowrap transition-colors ${
            activeTab === 'enrolment'
              ? 'border-[#0B3C5D] text-[#0B3C5D]'
              : 'border-transparent text-gray-500 hover:text-gray-800'
          }`}
        >
          Enrolment &amp; Intake Utilization
        </button>

        {isAicte && (
          <button
            onClick={() => setActiveTab('discrepancies')}
            className={`px-4 py-2 text-xs md:text-sm font-semibold border-b-2 whitespace-nowrap transition-colors ${
              activeTab === 'discrepancies'
                ? 'border-red-700 text-red-700'
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
          >
            Intake Discrepancies &amp; Breaches
          </button>
        )}

        {isAicte && (
          <button
            onClick={() => setActiveTab('anomalies')}
            className={`px-4 py-2 text-xs md:text-sm font-semibold border-b-2 whitespace-nowrap transition-colors ${
              activeTab === 'anomalies'
                ? 'border-amber-600 text-amber-700'
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
          >
            Explainable Anomaly Scan
          </button>
        )}

        <button
          onClick={() => setActiveTab('findings')}
          className={`px-4 py-2 text-xs md:text-sm font-semibold border-b-2 whitespace-nowrap transition-colors ${
            activeTab === 'findings'
              ? 'border-[#0B3C5D] text-[#0B3C5D]'
              : 'border-transparent text-gray-500 hover:text-gray-800'
          }`}
        >
          Validation Errors &amp; Findings
        </button>
      </div>

      {/* Report Content */}
      <div className="bg-white rounded-b-lg border border-[#D6DCE4] shadow-sm p-4">
        {loading ? (
          <div className="py-12 text-center text-gray-500 text-sm">
            <div className="w-8 h-8 border-4 border-[#0B3C5D] border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading regulatory records...
          </div>
        ) : activeTab === 'enrolment' ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-[#EEF5FA] border-b border-[#D6DCE4] text-[#0B3C5D] font-bold">
                  <th className="p-3">AICTE ID</th>
                  <th className="p-3">Institution Name</th>
                  <th className="p-3">State</th>
                  <th className="p-3">Programme</th>
                  <th className="p-3 text-right">Approved Intake</th>
                  <th className="p-3 text-right">Enrolled</th>
                  <th className="p-3 text-right">Verified</th>
                  <th className="p-3 text-right">Utilization %</th>
                  <th className="p-3 text-right">Breach Excess</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {reportData.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="p-6 text-center text-gray-500">
                      No enrolment records found.
                    </td>
                  </tr>
                ) : (
                  reportData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="p-3 font-mono font-medium text-gray-700">{row.aicte_id}</td>
                      <td className="p-3 font-semibold text-gray-800">{row.institution_name}</td>
                      <td className="p-3 text-gray-600">{row.state}</td>
                      <td className="p-3 text-gray-700">{row.programme}</td>
                      <td className="p-3 text-right font-medium">{row.approved_intake}</td>
                      <td className="p-3 text-right font-bold text-gray-900">{row.enrolled_students}</td>
                      <td className="p-3 text-right text-emerald-700 font-semibold">{row.verified_students}</td>
                      <td className="p-3 text-right">
                        <span
                          className={`font-semibold px-2 py-0.5 rounded ${
                            row.utilization_pct > 100
                              ? 'bg-red-100 text-red-800'
                              : row.utilization_pct >= 80
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          {row.utilization_pct}%
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        {row.capacity_breach_excess > 0 ? (
                          <span className="font-bold text-red-600">+{row.capacity_breach_excess}</span>
                        ) : (
                          <span className="text-gray-400">0</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        ) : activeTab === 'discrepancies' ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-red-50 border-b border-red-200 text-red-900 font-bold">
                  <th className="p-3">AICTE ID</th>
                  <th className="p-3">Institution Name</th>
                  <th className="p-3">Programme</th>
                  <th className="p-3 text-right">Approved Intake</th>
                  <th className="p-3 text-right">Actual Enrolment</th>
                  <th className="p-3 text-right">Excess Count</th>
                  <th className="p-3 text-right">Exceeded %</th>
                  <th className="p-3">Regulatory Enforcement</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {reportData.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="p-6 text-center text-gray-500">
                      No intake discrepancies detected across configured institutions.
                    </td>
                  </tr>
                ) : (
                  reportData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-red-50/40">
                      <td className="p-3 font-mono font-medium text-gray-700">{row.aicte_id}</td>
                      <td className="p-3 font-semibold text-gray-900">{row.institution_name}</td>
                      <td className="p-3 text-gray-700">{row.programme}</td>
                      <td className="p-3 text-right font-medium">{row.approved_intake}</td>
                      <td className="p-3 text-right font-bold text-red-700">{row.actual_enrolment}</td>
                      <td className="p-3 text-right font-black text-red-800">+{row.excess_count}</td>
                      <td className="p-3 text-right font-semibold text-red-700">+{row.excess_percentage}%</td>
                      <td className="p-3">
                        <span className="bg-red-100 text-red-900 px-2 py-0.5 rounded font-bold text-[11px] border border-red-300">
                          {row.regulatory_action_required}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        ) : activeTab === 'anomalies' ? (
          <div className="space-y-4">
            {anomalyData.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
                <p className="font-semibold text-gray-700">No statistical anomalies detected.</p>
                <p className="text-xs text-gray-400 mt-1">All institutional enrolment profiles conform to baseline tolerances.</p>
              </div>
            ) : (
              anomalyData.map((anom, idx) => (
                <div key={idx} className="p-4 rounded border border-amber-300 bg-amber-50/50">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="bg-amber-600 text-white font-bold text-[10px] px-2 py-0.5 rounded uppercase">
                          {anom.anomaly_type}
                        </span>
                        <h4 className="font-bold text-sm text-gray-900">{anom.title}</h4>
                      </div>
                      <p className="text-xs text-gray-700 mt-2 leading-relaxed">{anom.explanation}</p>
                    </div>

                    <span className="bg-red-100 text-red-800 border border-red-300 font-bold text-xs px-2.5 py-1 rounded shrink-0 uppercase">
                      {anom.severity}
                    </span>
                  </div>

                  {anom.metrics && (
                    <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs bg-white p-2.5 rounded border border-amber-200">
                      {Object.entries(anom.metrics).map(([k, v]) => (
                        <div key={k}>
                          <span className="text-gray-400 text-[10px] uppercase font-semibold">{k.replace('_', ' ')}</span>
                          <p className="font-mono font-bold text-gray-800">{String(v)}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-[#EEF5FA] border-b border-[#D6DCE4] text-[#0B3C5D] font-bold">
                  <th className="p-3">Error Code</th>
                  <th className="p-3">Field</th>
                  <th className="p-3">Severity</th>
                  <th className="p-3">Row #</th>
                  <th className="p-3">Message</th>
                  <th className="p-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {reportData.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-gray-500">
                      No validation findings logged.
                    </td>
                  </tr>
                ) : (
                  reportData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="p-3 font-mono font-bold text-gray-800">{row.error_code}</td>
                      <td className="p-3 font-mono text-gray-600">{row.field_name}</td>
                      <td className="p-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            row.severity === 'error'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {row.severity?.toUpperCase()}
                        </span>
                      </td>
                      <td className="p-3 font-mono">{row.row_number}</td>
                      <td className="p-3 text-gray-800">{row.message}</td>
                      <td className="p-3 font-mono text-gray-500 text-[11px]">
                        {row.created_at ? new Date(row.created_at).toLocaleString() : ''}
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

