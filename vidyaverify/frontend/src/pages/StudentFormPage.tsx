import { useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { studentsApi, institutionsApi } from '@/api'
import { useAuth } from '@/hooks/useAuth'
import { ArrowLeft, Save } from 'lucide-react'

const schema = z.object({
  full_name: z.string().min(2, 'Full name is required'),
  institution_id: z.string().uuid('Invalid institution'),
  programme_id: z.string().uuid().optional().or(z.literal('')),
  academic_year_id: z.string().uuid().optional().or(z.literal('')),
  enrolment_number: z.string().optional(),
  apaar_id: z.string().optional(),
  date_of_birth: z.string().optional(),
  gender: z.string().optional(),
  email: z.string().email().optional().or(z.literal('')),
  phone: z.string().optional(),
  admission_date: z.string().optional(),
  admission_category: z.string().default('general'),
  enrolment_status: z.string().default('active'),
  is_supernumerary: z.boolean().default(false),
  is_nri: z.boolean().default(false),
  is_oci: z.boolean().default(false),
  is_foreign_national: z.boolean().default(false),
  is_pwd: z.boolean().default(false),
})

type FormData = z.infer<typeof schema>

function FormField({ label, error, children }: { label: string; error?: any; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1.5">{label}</label>
      {children}
      {error && <p className="mt-1 text-xs text-red-600">{typeof error === 'string' ? error : error?.message || String(error)}</p>}
    </div>
  )
}

const inputClass = "w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"

export default function StudentFormPage() {
  const { id } = useParams<{ id: string }>()
  const isEdit = !!id
  const { user } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const defaultInstId = user?.institution_id ?? ''

  const { data: student } = useQuery({
    queryKey: ['student', id],
    queryFn: () => studentsApi.get(id!),
    enabled: isEdit,
  })

  const { data: institutionsData } = useQuery({
    queryKey: ['institutions', 1, ''],
    queryFn: () => institutionsApi.list({ page: 1, size: 100 }),
  })

  const { register, handleSubmit, watch, reset, formState: { errors } } = useForm<any>({
    resolver: zodResolver(schema),
    defaultValues: { institution_id: defaultInstId, admission_category: 'general', enrolment_status: 'active' },
  })

  const watchedInstId = watch('institution_id')
  const { data: programmes } = useQuery({
    queryKey: ['programmes', watchedInstId],
    queryFn: () => institutionsApi.programmes(watchedInstId),
    enabled: !!watchedInstId,
  })
  const { data: academicYears } = useQuery({
    queryKey: ['academic-years', watchedInstId],
    queryFn: () => institutionsApi.academicYears(watchedInstId),
    enabled: !!watchedInstId,
  })

  useEffect(() => {
    if (student) {
      reset({
        full_name: student.full_name,
        institution_id: student.institution_id,
        programme_id: student.programme_id ?? '',
        academic_year_id: student.academic_year_id ?? '',
        enrolment_number: student.enrolment_number ?? '',
        date_of_birth: student.date_of_birth ?? '',
        gender: student.gender ?? '',
        email: student.email ?? '',
        phone: student.phone ?? '',
        admission_date: student.admission_date ?? '',
        admission_category: student.admission_category,
        enrolment_status: student.enrolment_status,
        is_supernumerary: student.is_supernumerary,
        is_nri: student.is_nri,
        is_oci: student.is_oci,
        is_foreign_national: student.is_foreign_national,
        is_pwd: student.is_pwd,
      })
    }
  }, [student, reset])

  const mutation = useMutation({
    mutationFn: (data: FormData) => {
      const cleaned = {
        ...data,
        programme_id: data.programme_id || undefined,
        academic_year_id: data.academic_year_id || undefined,
        apaar_id: data.apaar_id || undefined,
      }
      return isEdit ? studentsApi.update(id!, cleaned as any) : studentsApi.create(cleaned as any)
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['students'] })
      navigate(`/students/${result.id}`)
    },
  })

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <Link to={isEdit ? `/students/${id}` : '/students'}
        className="flex items-center gap-1 text-slate-500 hover:text-slate-700 text-sm mb-6">
        <ArrowLeft size={14} /> Back
      </Link>

      <h1 className="text-2xl font-bold text-slate-800 mb-6">
        {isEdit ? 'Edit Student Record' : 'Add New Student'}
      </h1>

      {mutation.isError && (
        <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          {(mutation.error as any)?.response?.data?.detail ?? 'An error occurred. Please try again.'}
        </div>
      )}

      <form onSubmit={handleSubmit((d: any) => mutation.mutate(d))} className="space-y-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="font-semibold text-slate-700 mb-4">Personal Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField label="Full Name *" error={errors.full_name?.message}>
              <input {...register('full_name')} className={inputClass} placeholder="Student's full legal name" />
            </FormField>
            <FormField label="Date of Birth">
              <input {...register('date_of_birth')} type="date" className={inputClass} />
            </FormField>
            <FormField label="Gender">
              <select {...register('gender')} className={inputClass}>
                <option value="">Select gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Transgender">Transgender</option>
                <option value="Other">Other</option>
              </select>
            </FormField>
            <FormField label="Email">
              <input {...register('email')} type="email" className={inputClass} placeholder="student@example.com" />
            </FormField>
            <FormField label="Phone">
              <input {...register('phone')} className={inputClass} placeholder="10-digit mobile number" />
            </FormField>
            <FormField label="APAAR ID">
              <input {...register('apaar_id')} className={inputClass} placeholder="12-digit APAAR ID" />
              <p className="text-xs text-slate-400 mt-1">Will be hashed and masked before storage</p>
            </FormField>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="font-semibold text-slate-700 mb-4">Enrolment Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField label="Institution *" error={errors.institution_id?.message}>
              <select {...register('institution_id')} className={inputClass}
                disabled={['college_admin', 'admission_staff'].includes(user?.role ?? '')}>
                <option value="">Select institution</option>
                {institutionsData?.items.map(i => (
                  <option key={i.id} value={i.id}>{i.name}</option>
                ))}
              </select>
            </FormField>
            <FormField label="Programme">
              <select {...register('programme_id')} className={inputClass}>
                <option value="">Select programme</option>
                {programmes?.map(p => (
                  <option key={p.id} value={p.id}>{p.name} ({p.code})</option>
                ))}
              </select>
            </FormField>
            <FormField label="Academic Year">
              <select {...register('academic_year_id')} className={inputClass}>
                <option value="">Select academic year</option>
                {academicYears?.map(ay => (
                  <option key={ay.id} value={ay.id}>{ay.label}{ay.is_current ? ' (Current)' : ''}</option>
                ))}
              </select>
            </FormField>
            <FormField label="Enrolment Number">
              <input {...register('enrolment_number')} className={inputClass} placeholder="e.g. 2024CS001" />
            </FormField>
            <FormField label="Admission Date">
              <input {...register('admission_date')} type="date" className={inputClass} />
            </FormField>
            <FormField label="Admission Category">
              <select {...register('admission_category')} className={inputClass}>
                <option value="general">General</option>
                <option value="obc">OBC</option>
                <option value="sc">SC</option>
                <option value="st">ST</option>
                <option value="ews">EWS</option>
                <option value="nri">NRI</option>
                <option value="oci">OCI</option>
                <option value="foreign_national">Foreign National</option>
                <option value="management_quota">Management Quota</option>
                <option value="ph">Persons with Disability</option>
              </select>
            </FormField>
            <FormField label="Enrolment Status">
              <select {...register('enrolment_status')} className={inputClass}>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="transferred">Transferred</option>
                <option value="graduated">Graduated</option>
                <option value="dropped">Dropped</option>
                <option value="suspended">Suspended</option>
              </select>
            </FormField>
          </div>

          <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3">
            {([
              ['is_supernumerary', 'Supernumerary Seat'],
              ['is_nri', 'NRI'],
              ['is_oci', 'OCI'],
              ['is_foreign_national', 'Foreign National'],
              ['is_pwd', 'Person with Disability'],
            ] as [keyof FormData, string][]).map(([field, label]) => (
              <label key={field} className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
                <input type="checkbox" {...register(field as any)} className="rounded border-slate-300" />
                {label}
              </label>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <Link to={isEdit ? `/students/${id}` : '/students'}
            className="px-4 py-2 border border-slate-200 rounded-lg text-sm hover:bg-slate-50">
            Cancel
          </Link>
          <button type="submit" disabled={mutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-60">
            <Save size={16} />
            {mutation.isPending ? 'Saving…' : (isEdit ? 'Save Changes' : 'Create Student')}
          </button>
        </div>
      </form>
    </div>
  )
}
