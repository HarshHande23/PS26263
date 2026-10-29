import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Building2,
  Users,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet,
  History,
} from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

export const GovernmentNavigation: React.FC = () => {
  const { user } = useAuth()
  if (!user) return null

  const isAicte = user.role === 'super_admin' || user.role === 'aicte_admin'

  const navItems = [
    { label: 'Dashboard', to: '/', icon: LayoutDashboard },
    ...(isAicte ? [{ label: 'Institutions', to: '/institutions', icon: Building2 }] : []),
    { label: 'Student Enrolments', to: '/students', icon: Users },
    { label: 'Bulk Import', to: '/upload', icon: UploadCloud },
    { label: 'Validation & Duplicates', to: '/findings', icon: CheckCircle2 },
    { label: 'Alerts & Anomalies', to: '/alerts', icon: AlertTriangle },
    { label: 'Compliance Reports', to: '/reports', icon: FileSpreadsheet },
    ...(isAicte ? [{ label: 'Audit Trail', to: '/audit-logs', icon: History }] : []),
  ]

  return (
    <nav className="bg-[#0B3C5D] text-white shadow-md border-b-2 border-[#FF9933] sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 flex items-center overflow-x-auto no-scrollbar">
        <div className="flex items-center space-x-1 py-1">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-2 text-xs md:text-sm font-semibold rounded transition-colors whitespace-nowrap ${
                    isActive
                      ? 'bg-[#1D4E89] text-white shadow-inner border-b-2 border-[#FF9933]'
                      : 'text-gray-200 hover:bg-[#0E4A73] hover:text-white'
                  }`
                }
              >
                <Icon className="w-4 h-4 opacity-90" />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
