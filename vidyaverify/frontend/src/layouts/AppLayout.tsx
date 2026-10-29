import React from 'react'
import { Outlet } from 'react-router-dom'
import { UtilityBar } from '@/components/gov/UtilityBar'
import { GovernmentHeader } from '@/components/gov/GovernmentHeader'
import { GovernmentNavigation } from '@/components/gov/GovernmentNavigation'
import { GovernmentFooter } from '@/components/gov/GovernmentFooter'

export default function AppLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-[#F5F6F8] text-gray-800 antialiased">
      {/* 1. Official Utility Bar */}
      <UtilityBar />

      {/* 2. Tricolour & National Portal Header */}
      <GovernmentHeader />

      {/* 3. Deep Navy Government Navigation */}
      <GovernmentNavigation />

      {/* 4. Main Portal Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        <Outlet />
      </main>

      {/* 5. Official Regulatory Footer */}
      <GovernmentFooter />
    </div>
  )
}
