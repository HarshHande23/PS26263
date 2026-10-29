import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { uploadsApi } from '@/api'
import {
  FileSpreadsheet, Download, ArrowLeft, CheckCircle,
  AlertTriangle, AlertCircle, Clock, Check, XCircle
} from 'lucide-react'

export default function SubmissionDetailPage() {
  const { id } = useParams<{ id: string }>()

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
        <Link to="/upload" className="inline-flex items-center gap-2 mt-4 text-sm text-indigo-600 hover:text-indigo-800">
          <ArrowLeft size={16} /> Back to Uploads
        </Link>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <Link to="/upload" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-3">
          <ArrowLeft size={16} /> Back to Uploads
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
              <FileSpreadsheet className="text-indigo-600" size={28} />
              {submission.filename}
            </h1>
            <p className="text-slate-500 text-sm mt-1">
              Submission ID: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs">{submission.id}</code> &bull;{' '}
              Uploaded: {new Date(submission.created_at).toLocaleString()}
            </p>
          </div>

          {submission.invalid_rows > 0 && (
            <a
              href={uploadsApi.rejectedExportUrl(submission.id)}
              download={`rejected_rows_${submission.id}.csv`}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100"
            >
              <Download size={16} />
              Export Rejected Rows (.CSV)
            </a>
          )}
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-xs text-slate-500">Total Rows</div>
          <div className="text-2xl font-bold text-slate-800 mt-1">{submission.total_rows}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-xs text-emerald-600 font-medium">Valid Rows</div>
          <div className="text-2xl font-bold text-emerald-700 mt-1">{submission.valid_rows}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-xs text-indigo-600 font-medium">Imported</div>
          <div className="text-2xl font-bold text-indigo-700 mt-1">{submission.imported_rows}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-xs text-amber-600 font-medium">Duplicates</div>
          <div className="text-2xl font-bold text-amber-600 mt-1">{submission.duplicate_rows}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <div className="text-xs text-red-600 font-medium">Invalid Rows</div>
          <div className="text-2xl font-bold text-red-600 mt-1">{submission.invalid_rows}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200">
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
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-800 flex items-center gap-2">
            <XCircle size={18} className="text-red-500" />
            Validation Findings & Row Errors ({errors?.length ?? 0})
          </h2>
          <span className="text-xs text-slate-500">Every rejected row is captured with exact reasons</span>
        </div>

        {loadingErrors ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading row errors...</div>
        ) : !errors || errors.length === 0 ? (
          <div className="p-8 text-center text-emerald-600 text-sm flex flex-col items-center gap-2">
            <Check size={24} className="text-emerald-500" />
            <span className="font-medium">No row errors recorded! All submitted rows passed schema validation.</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-medium">
                <tr>
                  <th className="px-5 py-3 w-20">Row #</th>
                  <th className="px-5 py-3">Error Type</th>
                  <th className="px-5 py-3">Field</th>
                  <th className="px-5 py-3">Reason / Message</th>
                  <th className="px-5 py-3">Submitted Row Preview</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {errors.map((err) => (
                  <tr key={err.id} className="hover:bg-slate-50/70">
                    <td className="px-5 py-3 font-semibold text-slate-900">{err.row_number}</td>
                    <td className="px-5 py-3">
                      <span className="px-2 py-0.5 bg-red-100 text-red-800 rounded text-xs font-mono">
                        {err.error_type}
                      </span>
                    </td>
                    <td className="px-5 py-3 font-medium text-slate-800">{err.field_name || '—'}</td>
                    <td className="px-5 py-3 text-red-700">{err.error_message}</td>
                    <td className="px-5 py-3 font-mono text-xs text-slate-500 max-w-xs truncate">
                      {err.row_data ? JSON.stringify(err.row_data) : '—'}
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
