import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
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
  const location = useLocation()
  if (!user) return null

  const isAicte = user.role === 'super_admin' || user.role === 'aicte_admin'

  // Resolve the canonical dashboard path for the current user
  const dashboardPath = isAicte ? '/dashboard/aicte' : '/dashboard/college'

  // Determine if dashboard tab is active — matches any dashboard sub-route
  const isDashboardActive =
    location.pathname === '/' ||
    location.pathname.startsWith('/dashboard')

  const navItems = [
    {
      label: 'Dashboard',
      to: dashboardPath,
      icon: LayoutDashboard,
      isActive: isDashboardActive,
    },
    ...(isAicte
      ? [
          {
            label: 'Institutions',
            to: '/institutions',
            icon: Building2,
            isActive: undefined, // use NavLink default
          },
        ]
      : []),
    {
      label: 'Student Enrolments',
      to: '/students',
      icon: Users,
      isActive: undefined,
    },
    {
      label: 'Bulk Import',
      to: '/bulk-import',
      icon: UploadCloud,
      isActive: location.pathname.startsWith('/bulk-import') || location.pathname.startsWith('/upload'),
    },
    {
      label: 'Validation & Duplicates',
      to: '/validation-duplicates',
      icon: CheckCircle2,
      isActive: location.pathname.startsWith('/validation-duplicates') || location.pathname.startsWith('/findings'),
    },
    {
      label: 'Alerts & Anomalies',
      to: '/alerts-anomalies',
      icon: AlertTriangle,
      isActive: location.pathname.startsWith('/alerts-anomalies') || location.pathname.startsWith('/alerts'),
    },
    {
      label: 'Compliance Reports',
      to: '/compliance-reports',
      icon: FileSpreadsheet,
      isActive: location.pathname.startsWith('/compliance-reports') || location.pathname.startsWith('/reports'),
    },
    ...(isAicte
      ? [
          {
            label: 'Audit Trail',
            to: '/audit-logs',
            icon: History,
            isActive: undefined,
          },
        ]
      : []),
  ]

  const activeClass = 'bg-[#1D4E89] text-white shadow-inner border-b-2 border-[#FF9933]'
  const inactiveClass = 'text-gray-200 hover:bg-[#0E4A73] hover:text-white'
  const baseClass = 'flex items-center gap-1.5 px-3 py-2 text-xs md:text-sm font-semibold rounded transition-colors whitespace-nowrap'

  return (
    <nav className="bg-[#0B3C5D] text-white shadow-md border-b-2 border-[#FF9933] sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 flex items-center overflow-x-auto no-scrollbar">
        <div className="flex items-center space-x-1 py-1">
          {navItems.map((item) => {
            const Icon = item.icon
            // Items with a manual isActive override (e.g. Dashboard, Bulk Import, etc.)
            if (item.isActive !== undefined) {
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={`${baseClass} ${item.isActive ? activeClass : inactiveClass}`}
                >
                  <Icon className="w-4 h-4 opacity-90" />
                  <span>{item.label}</span>
                </NavLink>
              )
            }
            // Items using NavLink's automatic active detection
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `${baseClass} ${isActive ? activeClass : inactiveClass}`
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
