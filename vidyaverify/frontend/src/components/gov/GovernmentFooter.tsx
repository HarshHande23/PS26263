import React from 'react'
import { ShieldCheck, Info } from 'lucide-react'

export const GovernmentFooter: React.FC = () => {
  return (
    <footer className="bg-[#072438] text-gray-300 text-xs mt-auto border-t-4 border-[#0B3C5D]">
      {/* Simulation & Prototype Notice */}
      <div className="bg-[#0A2E46] border-b border-[#0B3C5D] py-2.5 px-4">
        <div className="max-w-7xl mx-auto flex items-center justify-center gap-2 text-center text-amber-200">
          <Info className="w-4 h-4 shrink-0" />
          <span>
            <strong>Official Synthetic Testing Prototype:</strong> All data, APAAR records, and verification results
            displayed in this system are synthetic test fixtures. No real government databases or live student PII are accessed.
          </span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <div className="flex items-center gap-2 text-white font-bold text-sm mb-2">
            <ShieldCheck className="w-4 h-4 text-[#FF9933]" />
            All India Council for Technical Education (AICTE)
          </div>
          <p className="text-gray-400 leading-relaxed text-[11px]">
            Nelson Mandela Marg, Vasant Kunj, New Delhi-110070. Developed for AICTE Problem Statement 26263:
            APAAR-Based Student Data Management &amp; Regulatory Verification Platform.
          </p>
        </div>

        <div>
          <h4 className="text-white font-semibold text-xs mb-2 uppercase tracking-wider">Regulatory Compliance</h4>
          <ul className="space-y-1 text-gray-400 text-[11px]">
            <li>&bull; Strict Zero-Plaintext APAAR Storage (SHA-256 Hash + Salt)</li>
            <li>&bull; Non-Repudiable Cryptographic Token QR Issuance</li>
            <li>&bull; Multi-Tenant Institution Isolation &amp; Audit Trail</li>
            <li>&bull; Explainable Statistical Anomaly &amp; Intake Breach Engine</li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold text-xs mb-2 uppercase tracking-wider">System Information</h4>
          <p className="text-gray-400 text-[11px] mb-2">
            Build: VidyaVerify v2.0-rc &bull; Environment: Synthetic Test Lab
          </p>
          <div className="flex flex-wrap gap-3 text-gray-300 text-[11px]">
            <span className="hover:underline cursor-pointer">Terms of Service</span>
            <span>&bull;</span>
            <span className="hover:underline cursor-pointer">Security Policy</span>
            <span>&bull;</span>
            <span className="hover:underline cursor-pointer">Feedback &amp; Helpdesk</span>
          </div>
        </div>
      </div>

      <div className="bg-[#051B2A] py-3 text-center text-[11px] text-gray-400 border-t border-gray-800">
        &copy; {new Date().getFullYear()} All India Council for Technical Education. All Rights Reserved.
      </div>
    </footer>
  )
}
