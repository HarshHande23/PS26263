import React, { useState, useEffect } from 'react'

export const UtilityBar: React.FC = () => {
  const [fontSizeOffset, setFontSizeOffset] = useState<number>(0)
  const [highContrast, setHighContrast] = useState<boolean>(false)

  const adjustFontSize = (delta: number) => {
    const newOffset = Math.max(-2, Math.min(4, fontSizeOffset + delta))
    setFontSizeOffset(newOffset)
    document.documentElement.style.fontSize = `${16 + newOffset}px`
  }

  const toggleHighContrast = () => {
    const next = !highContrast
    setHighContrast(next)
    if (next) {
      document.body.classList.add('contrast-125')
    } else {
      document.body.classList.remove('contrast-125')
    }
  }

  return (
    <div className="bg-[#072438] text-[#D6DCE4] text-xs py-1.5 px-4 border-b border-[#0B3C5D]/60 select-none">
      <div className="max-w-7xl mx-auto flex flex-wrap justify-between items-center gap-2">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-white tracking-wide">भारत सरकार | Government of India</span>
          <span className="text-gray-400">|</span>
          <span className="text-gray-300">Ministry of Education &bull; AICTE</span>
          <span className="hidden md:inline-block bg-[#1D4E89] text-[10px] text-white px-2 py-0.5 rounded font-mono uppercase tracking-wider">
            SYNTHETIC PROTOTYPE &bull; PS 26263
          </span>
        </div>

        <div className="flex items-center gap-4 text-gray-300">
          <div className="flex items-center gap-1 bg-[#0A2E46] px-2 py-0.5 rounded border border-[#1D4E89]">
            <span className="text-[11px] text-gray-400 mr-1">Text:</span>
            <button
              onClick={() => adjustFontSize(-1)}
              className="px-1.5 hover:text-white font-bold"
              title="Decrease Font Size"
            >
              A-
            </button>
            <button
              onClick={() => {
                setFontSizeOffset(0)
                document.documentElement.style.fontSize = '16px'
              }}
              className="px-1.5 hover:text-white font-bold"
              title="Reset Font Size"
            >
              A
            </button>
            <button
              onClick={() => adjustFontSize(1)}
              className="px-1.5 hover:text-white font-bold"
              title="Increase Font Size"
            >
              A+
            </button>
          </div>

          <button
            onClick={toggleHighContrast}
            className={`px-2 py-0.5 rounded text-[11px] border transition-colors ${
              highContrast ? 'bg-amber-400 text-black border-amber-500 font-semibold' : 'hover:text-white border-[#1D4E89]'
            }`}
          >
            {highContrast ? 'Standard View' : 'High Contrast'}
          </button>

          <span className="text-[11px] text-gray-400 font-medium">English / हिन्दी</span>
        </div>
      </div>
    </div>
  )
}
