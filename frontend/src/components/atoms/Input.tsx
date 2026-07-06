import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string
}

export function Input({ error, className = '', ...props }: InputProps) {
  const base =
    'block w-full rounded-lg border px-3 py-2 text-sm shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500'
  const stateClass = error
    ? 'border-red-400 bg-red-50 focus:ring-red-400'
    : 'border-gray-300 bg-white hover:border-gray-400'

  return (
    <div className="w-full">
      <input className={`${base} ${stateClass} ${className}`} {...props} />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  )
}
