import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { uploadsApi } from '@/api'
import {
  FileSpreadsheet, Download, ArrowLeft, CheckCircle,
  AlertTriangle, AlertCircle, Clock, Check, XCircle, Filter, Loader2, Copy
} from 'lucide-react'

export default function SubmissionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [exporting, setExporting] = useState(false)
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'ERRORS' | 'DUPLICATES' | 'ANOMALIES'>('ALL')

  const { data: submission, isLoading: loadingSub, error: subError } = useQuery({
    queryKey: ['submission', id],
    queryFn: () => uploadsApi.get(id!),
    enabled: !!id,
  })

  const { data: errors, isLoading: loadingErrors } = useQuery({
    queryKey: ['submission-errors', id],
    queryFn: () => uploadsApi.errors(id!),
    enabled: !!id,
  })

  const handleExport = async () => {
    if (!submission) return
    setExporting(true)
    try {
      const blob = await uploadsApi.exportRejectedRows(submission.id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `validation_findings_${submission.filename || submission.id}.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Failed to export via API client, attempting fallback link:', err)
      const directUrl = uploadsApi.rejectedExportUrl(submission.id)
      window.open(directUrl, '_blank')
    } finally {
      setExporting(false)
    }
  }

  const isDuplicate = (errorType: string) => {
    const t = errorType.toUpperCase()
    return t.includes('DUP') || t.includes('COLLISION')
  }

  const isFatalError = (errorType: string) => {
    const t = errorType.toUpperCase()
    return t.includes('MISSING_NAME') || t.includes('MALFORMED_APAAR') || t.includes('FUTURE_DOB') || t.includes('REIMPORT')
  }

  const filteredErrors = useMemo(() => {
    if (!errors) return []
    if (activeFilter === 'ALL') return errors
    if (activeFilter === 'DUPLICATES') return errors.filter(e => isDuplicate(e.error_type))
    if (activeFilter === 'ERRORS') return errors.filter(e => isFatalError(e.error_type))
    if (activeFilter === 'ANOMALIES') return errors.filter(e => !isDuplicate(e.error_type) && !isFatalError(e.error_type))
    return errors
  }, [errors, activeFilter])

  const counts = useMemo(() => {
    if (!errors) return { all: 0, errors: 0, dups: 0, anomalies: 0 }
    return {
      all: errors.length,
      errors: errors.filter(e => isFatalError(e.error_type)).length,
      dups: errors.filter(e => isDuplicate(e.error_type)).length,
      anomalies: errors.filter(e => !isDuplicate(e.error_type) && !isFatalError(e.error_type)).length,
    }
  }, [errors])

  const getBadgeStyle = (errorType: string) => {
    if (isDuplicate(errorType)) {
      return 'bg-amber-100 text-amber-800 border-amber-300'
    }
    if (isFatalError(errorType)) {
      return 'bg-red-100 text-red-800 border-red-300'
    }
    if (errorType.toUpperCase().includes('INTAKE')) {
      return 'bg-purple-100 text-purple-800 border-purple-300'
    }
    return 'bg-blue-100 text-blue-800 border-blue-300'
  }

  if (loadingSub) {
    return <div className="p-8 text-center text-slate-500">Loading submission details...</div>
  }

  if (subError || !submission) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-3">
          <AlertCircle size={20} />
          <span>Failed to load submission #{id}. It may not exist or you lack permission.</span>
        </div>
        <Link to="/upload" className="inline-flex items-center gap-2 mt-4 text-sm text-[#1D4E89] hover:underline">
          <ArrowLeft size={16} /> Back to Uploads
        </Link>
      </div>
    )
  }

  const hasIssues = (submission.invalid_rows > 0) || (submission.duplicate_rows > 0) || (errors && errors.length > 0)

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <Link to="/upload" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-3">
          <ArrowLeft size={16} /> Back to Uploads
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
              <FileSpreadsheet className="text-[#1D4E89]" size={28} />
              {submission.filename}
            </h1>
            <p className="text-slate-500 text-sm mt-1">
              Submission ID: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs">{submission.id}</code> &bull;{' '}
              Uploaded: {new Date(submission.created_at).toLocaleString()}
            </p>
          </div>

          {hasIssues && (
            <button
              onClick={handleExport}
              disabled={exporting}
              className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold text-white bg-[#1D4E89] hover:bg-[#0B3C5D] active:scale-95 transition-all rounded-lg shadow-sm border border-[#0B3C5D] disabled:opacity-50 cursor-pointer"
            >
              {exporting ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Generating Export CSV...
                </>
              ) : (
                <>
                  <Download size={16} />
                  Export Validation Findings (.CSV)
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-500 font-medium">Total Rows</div>
          <div className="text-2xl font-bold text-slate-800 mt-1">{submission.total_rows}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs text-emerald-600 font-medium">Valid Rows</div>
          <div className="text-2xl font-bold text-emerald-700 mt-1">{submission.valid_rows}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs text-[#1D4E89] font-medium">Imported</div>
          <div className="text-2xl font-bold text-[#1D4E89] mt-1">{submission.imported_rows}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs text-amber-600 font-medium">Duplicates</div>
          <div className="text-2xl font-bold text-amber-600 mt-1">{submission.duplicate_rows}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs text-red-600 font-medium">Invalid Rows</div>
          <div className="text-2xl font-bold text-red-600 mt-1">{submission.invalid_rows}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="text-xs text-purple-600 font-medium">Intake Exceeded</div>
          <div className="text-2xl font-bold text-purple-600 mt-1">{submission.intake_exceeded_rows}</div>
        </div>
      </div>

      {/* Status banner */}
      <div className={`p-4 rounded-xl border flex items-center gap-3 ${
        submission.status === 'completed'
          ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
          : submission.status === 'failed'
          ? 'bg-red-50 border-red-200 text-red-800'
          : 'bg-amber-50 border-amber-200 text-amber-800'
      }`}>
        {submission.status === 'completed' ? (
          <CheckCircle size={20} className="shrink-0 text-emerald-600" />
        ) : (
          <AlertTriangle size={20} className="shrink-0 text-amber-600" />
        )}
        <div className="text-sm">
          <span className="font-semibold uppercase tracking-wider text-xs block">Status: {submission.status}</span>
          {submission.error_summary ? (
            <p className="mt-0.5">{submission.error_summary}</p>
          ) : (
            <p className="mt-0.5">Import processing finished successfully without fatal file errors.</p>
          )}
        </div>
      </div>

      {/* Row Errors Breakdown Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-slate-800 flex items-center gap-2">
              <XCircle size={18} className="text-red-500" />
              Validation Findings, Duplicates & Anomalies ({errors?.length ?? 0})
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Comprehensive breakdown of all rejected rows, APAAR duplicate collisions, and data quality anomalies.
            </p>
          </div>

          {/* Filter Pills */}
          {errors && errors.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 text-xs bg-slate-100 p-1 rounded-lg">
              <button
                onClick={() => setActiveFilter('ALL')}
                className={`px-3 py-1.5 font-medium rounded-md transition-colors ${
                  activeFilter === 'ALL'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                All Issues ({counts.all})
              </button>
              <button
                onClick={() => setActiveFilter('ERRORS')}
                className={`px-3 py-1.5 font-medium rounded-md transition-colors ${
                  activeFilter === 'ERRORS'
                    ? 'bg-white text-red-700 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Schema Errors ({counts.errors})
              </button>
              <button
                onClick={() => setActiveFilter('DUPLICATES')}
                className={`px-3 py-1.5 font-medium rounded-md transition-colors ${
                  activeFilter === 'DUPLICATES'
                    ? 'bg-white text-amber-700 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Duplicates ({counts.dups})
              </button>
              <button
                onClick={() => setActiveFilter('ANOMALIES')}
                className={`px-3 py-1.5 font-medium rounded-md transition-colors ${
                  activeFilter === 'ANOMALIES'
                    ? 'bg-white text-blue-700 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Anomalies & Warnings ({counts.anomalies})
              </button>
            </div>
          )}
        </div>

        {loadingErrors ? (
          <div className="p-8 text-center text-slate-400 text-sm flex items-center justify-center gap-2">
            <Loader2 size={16} className="animate-spin text-[#1D4E89]" />
            Loading validation findings...
          </div>
        ) : !errors || errors.length === 0 ? (
          <div className="p-8 text-center text-emerald-600 text-sm flex flex-col items-center gap-2">
            <Check size={24} className="text-emerald-500" />
            <span className="font-medium">No errors or anomalies recorded! All submitted rows passed validation cleanly.</span>
          </div>
        ) : filteredErrors.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">
            No issues match the selected filter tab.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-medium">
                <tr>
                  <th className="px-5 py-3 w-20">Row #</th>
                  <th className="px-5 py-3">Category & Rule</th>
                  <th className="px-5 py-3">Field</th>
                  <th className="px-5 py-3">Reason / Regulatory Finding</th>
                  <th className="px-5 py-3">Submitted Row Data</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {filteredErrors.map((err) => (
                  <tr key={err.id} className="hover:bg-slate-50/70">
                    <td className="px-5 py-3 font-semibold text-slate-900">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 text-slate-700 font-mono text-xs">
                        {err.row_number}
                      </span>
                    </td>
                    <td className="px-5 py-3 whitespace-nowrap">
                      <span className={`px-2.5 py-1 rounded-md text-xs font-mono font-semibold border ${getBadgeStyle(err.error_type)}`}>
                        {err.error_type}
                      </span>
                    </td>
                    <td className="px-5 py-3 font-medium text-slate-800">
                      {err.field_name ? (
                        <code className="text-xs bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded">
                          {err.field_name}
                        </code>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td className="px-5 py-3 text-slate-900 font-medium max-w-md">
                      {err.error_message}
                    </td>
                    <td className="px-5 py-3 text-xs text-slate-600 max-w-sm">
                      {err.row_data ? (
                        <div className="bg-slate-50 p-2 rounded border border-slate-100 text-slate-700 font-sans space-y-0.5">
                          {Boolean(err.row_data.full_name) && (
                            <div><strong className="text-slate-900">Name:</strong> {String(err.row_data.full_name)}</div>
                          )}
                          {Boolean(err.row_data.apaar_id) && (
                            <div><strong className="text-slate-900">APAAR:</strong> <code className="font-mono text-indigo-700">{String(err.row_data.apaar_id)}</code></div>
                          )}
                          {Boolean(err.row_data.email) && (
                            <div><strong className="text-slate-900">Email:</strong> {String(err.row_data.email)}</div>
                          )}
                          {Boolean(err.row_data.enrolment_number) && (
                            <div><strong className="text-slate-900">Enrolment:</strong> {String(err.row_data.enrolment_number)}</div>
                          )}
                          {Boolean(err.row_data.programme_code) && (
                            <div><strong className="text-slate-900">Programme:</strong> {String(err.row_data.programme_code)}</div>
                          )}
                          {Boolean(err.row_data.date_of_birth) && (
                            <div><strong className="text-slate-900">DOB:</strong> {String(err.row_data.date_of_birth)}</div>
                          )}
                        </div>
                      ) : (
                        '—'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
