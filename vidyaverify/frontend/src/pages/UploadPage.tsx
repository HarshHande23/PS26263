import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { uploadsApi, institutionsApi } from '@/api'
import { useAuth } from '@/hooks/useAuth'
import { Link, useNavigate } from 'react-router-dom'
import { Upload, FileSpreadsheet, Download, CheckCircle, AlertTriangle, AlertCircle, ArrowRight, Clock, FileText } from 'lucide-react'

export default function UploadPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedInstitutionId, setSelectedInstitutionId] = useState<string>(user?.institution_id || '')
  const [dragOver, setDragOver] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)

  const isCrossInstAdmin = ['super_admin', 'aicte_admin'].includes(user?.role || '')

  const { data: institutionsData } = useQuery({
    queryKey: ['institutions', 'simple-list'],
    queryFn: () => institutionsApi.list({ size: 100 }),
    enabled: isCrossInstAdmin,
  })

  const { data: submissions, isLoading: loadingSubmissions } = useQuery({
    queryKey: ['uploads', selectedInstitutionId || user?.institution_id],
    queryFn: () => uploadsApi.list({
      institution_id: isCrossInstAdmin && selectedInstitutionId ? selectedInstitutionId : undefined
    }),
  })

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const instId = isCrossInstAdmin ? selectedInstitutionId : user?.institution_id || undefined
      return uploadsApi.upload(file, instId)
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['uploads'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      navigate(`/upload/${data.id}`)
    },
    onError: (err: any) => {
      setUploadError(err.response?.data?.detail || 'Failed to upload and process file. Please try again.')
    }
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (!file.name.match(/\.(csv|xlsx|xls)$/i)) {
        setUploadError('Only CSV and Excel (.xlsx, .xls) files are supported.')
        return
      }
      setSelectedFile(file)
      setUploadError(null)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (!file.name.match(/\.(csv|xlsx|xls)$/i)) {
        setUploadError('Only CSV and Excel (.xlsx, .xls) files are supported.')
        return
      }
      setSelectedFile(file)
      setUploadError(null)
    }
  }

  const handleUpload = () => {
    if (!selectedFile) return
    if (isCrossInstAdmin && !selectedInstitutionId) {
      setUploadError('Please select an institution to upload records for.')
      return
    }
    setUploadError(null)
    uploadMutation.mutate(selectedFile)
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Bulk Student Data Import</h1>
          <p className="text-slate-500 text-sm mt-1">
            Upload CSV or Excel spreadsheets to batch enroll students and run automated validation checks.
          </p>
        </div>
        <a
          href={uploadsApi.templateUrl()}
          download="apaar_import_template.csv"
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 shadow-sm"
        >
          <Download size={16} />
          Download Template
        </a>
      </div>

      {/* Upload Wizard Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Step 1: Select Institution & File</h2>

        {isCrossInstAdmin && (
          <div className="mb-5 max-w-md">
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Target Institution <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedInstitutionId}
              onChange={(e) => setSelectedInstitutionId(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select an institution...</option>
              {institutionsData?.items.map((inst) => (
                <option key={inst.id} value={inst.id}>
                  {inst.name} ({inst.aicte_id})
                </option>
              ))}
            </select>
          </div>
        )}

        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
            dragOver ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-300 hover:border-slate-400'
          }`}
        >
          <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-3">
            <Upload size={24} />
          </div>
          <div className="text-slate-800 font-medium mb-1">
            {selectedFile ? selectedFile.name : 'Choose a file or drag and drop'}
          </div>
          <p className="text-xs text-slate-500 mb-4">CSV or Excel files up to 10MB</p>

          <input
            id="file-upload"
            type="file"
            accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
            onChange={handleFileChange}
            className="hidden"
          />
          <label
            htmlFor="file-upload"
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 cursor-pointer"
          >
            Browse Computer
          </label>
        </div>

        {uploadError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-center gap-2">
            <AlertCircle size={16} className="shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploadMutation.isPending}
            className={`inline-flex items-center gap-2 px-6 py-2.5 text-sm font-medium text-white rounded-lg transition-colors ${
              !selectedFile || uploadMutation.isPending
                ? 'bg-slate-300 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 shadow'
            }`}
          >
            {uploadMutation.isPending ? 'Processing Import...' : 'Upload & Validate'}
            <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* Upload History */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
            <Clock size={18} className="text-slate-500" />
            Recent Submissions
          </h2>
        </div>

        {loadingSubmissions ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading submission history...</div>
        ) : !submissions || submissions.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">
            No bulk imports found. Upload your first CSV or XLSX file above.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-medium">
                <tr>
                  <th className="px-5 py-3">File Name</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Total Rows</th>
                  <th className="px-5 py-3">Valid / Imported</th>
                  <th className="px-5 py-3">Duplicates</th>
                  <th className="px-5 py-3">Errors</th>
                  <th className="px-5 py-3">Uploaded At</th>
                  <th className="px-5 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {submissions.map((sub) => (
                  <tr key={sub.id} className="hover:bg-slate-50/70">
                    <td className="px-5 py-3.5 font-medium text-slate-900 flex items-center gap-2">
                      <FileSpreadsheet size={16} className="text-emerald-600" />
                      {sub.filename}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        sub.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : sub.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}>
                        {sub.status}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">{sub.total_rows}</td>
                    <td className="px-5 py-3.5 text-emerald-600 font-medium">
                      {sub.imported_rows} / {sub.valid_rows}
                    </td>
                    <td className="px-5 py-3.5">
                      {sub.duplicate_rows > 0 ? (
                        <span className="text-amber-600 font-semibold">{sub.duplicate_rows}</span>
                      ) : (
                        '0'
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      {sub.invalid_rows > 0 ? (
                        <span className="text-red-600 font-semibold">{sub.invalid_rows}</span>
                      ) : (
                        '0'
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-slate-500 text-xs">
                      {new Date(sub.created_at).toLocaleString()}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        to={`/upload/${sub.id}`}
                        className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                      >
                        View Details &rarr;
                      </Link>
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
