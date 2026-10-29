import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import {
  LayoutDashboard, Building2, Users, Upload, AlertTriangle, Bell,
  LogOut, GraduationCap, ShieldCheck, ChevronRight, Menu, X
} from 'lucide-react'
import { useState } from 'react'
import type { UserRole } from '@/types'

const ROLE_LABELS: Record<UserRole, string> = {
  super_admin: 'Super Admin',
  aicte_admin: 'AICTE Admin',
  college_admin: 'College Admin',
  admission_staff: 'Admission Staff',
  authorized_verifier: 'Verifier',
  student: 'Student',
}

interface NavItem {
  label: string
  to: string
  icon: React.ReactNode
  roles?: UserRole[]
}

const NAV_ITEMS: NavItem[] = [
  {
    label: 'AICTE Dashboard',
    to: '/dashboard/aicte',
    icon: <ShieldCheck size={18} />,
    roles: ['super_admin', 'aicte_admin'],
  },
  {
    label: 'College Dashboard',
    to: '/dashboard/college',
    icon: <LayoutDashboard size={18} />,
  },
  {
    label: 'Institutions',
    to: '/institutions',
    icon: <Building2 size={18} />,
  },
  {
    label: 'Students',
    to: '/students',
    icon: <Users size={18} />,
    roles: ['super_admin', 'aicte_admin', 'college_admin', 'admission_staff', 'authorized_verifier'],
  },
  {
    label: 'Bulk Upload',
    to: '/upload',
    icon: <Upload size={18} />,
    roles: ['super_admin', 'aicte_admin', 'college_admin', 'admission_staff'],
  },
  {
    label: 'Validation Findings',
    to: '/findings',
    icon: <AlertTriangle size={18} />,
    roles: ['super_admin', 'aicte_admin', 'college_admin', 'admission_staff'],
  },
  {
    label: 'Alerts',
    to: '/alerts',
    icon: <Bell size={18} />,
    roles: ['super_admin', 'aicte_admin', 'college_admin'],
  },
]

export default function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const visibleNav = NAV_ITEMS.filter(
    (item) => !item.roles || (user && item.roles.includes(user.role))
  )

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-200 bg-navy-800 text-white flex flex-col flex-shrink-0`}>
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-navy-700">
          <div className="w-8 h-8 bg-blue-400 rounded flex items-center justify-center flex-shrink-0">
            <GraduationCap size={18} className="text-white" />
          </div>
          {sidebarOpen && (
            <div>
              <div className="font-bold text-sm">VidyaVerify</div>
              <div className="text-xs text-navy-300">AICTE Platform</div>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="ml-auto text-navy-300 hover:text-white"
          >
            {sidebarOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
          {visibleNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-navy-200 hover:bg-navy-700 hover:text-white'
                }`
              }
            >
              <span className="flex-shrink-0">{item.icon}</span>
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        {user && (
          <div className="border-t border-navy-700 p-3">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold">
                {user.full_name.charAt(0).toUpperCase()}
              </div>
              {sidebarOpen && (
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{user.full_name}</div>
                  <div className="text-xs text-navy-300">{ROLE_LABELS[user.role]}</div>
                </div>
              )}
              {sidebarOpen && (
                <button onClick={handleLogout} className="text-navy-300 hover:text-white" title="Logout">
                  <LogOut size={16} />
                </button>
              )}
            </div>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
