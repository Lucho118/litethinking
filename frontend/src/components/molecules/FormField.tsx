import React from 'react'
import { Input } from '@/components/atoms/Input'

interface FormFieldProps {
  label: string
  error?: string
  children?: React.ReactNode
  // Si no se pasan children, se renderiza un Input con inputProps
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>
}

export function FormField({ label, error, children, inputProps }: FormFieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      {children ?? <Input error={error} {...inputProps} />}
    </div>
  )
}
