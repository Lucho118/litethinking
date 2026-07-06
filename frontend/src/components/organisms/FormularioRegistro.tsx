import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/atoms/Button'
import { Input } from '@/components/atoms/Input'
import { FormField } from '@/components/molecules/FormField'

interface ApiError {
  response?: { data?: Record<string, string | string[]> }
}

// ─── Reglas de contraseña (espejo exacto del backend FuertePasswordValidator) ──
interface Requisito {
  label: string
  test: (pwd: string) => boolean
}

const REQUISITOS: Requisito[] = [
  { label: 'Mínimo 8 caracteres', test: (p) => p.length >= 8 },
  { label: 'Al menos una mayúscula', test: (p) => /[A-Z]/.test(p) },
  { label: 'Al menos un número', test: (p) => /\d/.test(p) },
  {
    label: 'Al menos un carácter especial (!@#$%...)',
    test: (p) => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(p),
  },
]

function PasswordRequisitos({ password }: { password: string }) {
  if (!password) return null
  return (
    <ul className="mt-2 flex flex-col gap-1">
      {REQUISITOS.map((r) => {
        const ok = r.test(password)
        return (
          <li key={r.label} className={`flex items-center gap-1.5 text-xs ${ok ? 'text-green-600' : 'text-gray-400'}`}>
            <span className={`flex-shrink-0 h-3.5 w-3.5 rounded-full flex items-center justify-center text-[10px] font-bold
              ${ok ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-400'}`}>
              {ok ? '✓' : '·'}
            </span>
            {r.label}
          </li>
        )
      })}
    </ul>
  )
}

export function FormularioRegistro() {
  const [form, setForm] = useState({
    email: '',
    nombre: '',
    apellido: '',
    password: '',
    password_confirmar: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  const register = useAuthStore((s) => s.register)
  const navigate = useNavigate()

  function set(field: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
    // Limpiar el error del campo al editar
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: '' }))
  }

  function validate(): boolean {
    const newErrors: Record<string, string> = {}
    if (!form.email) newErrors.email = 'El correo es requerido'
    for (const r of REQUISITOS) {
      if (!r.test(form.password)) {
        newErrors.password = r.label
        break
      }
    }
    if (form.password !== form.password_confirmar)
      newErrors.password_confirmar = 'Las contraseñas no coinciden'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      await register(
        form.email,
        form.password,
        form.password_confirmar,
        form.nombre,
        form.apellido,
      )
      navigate('/')
    } catch (err: unknown) {
      const apiErr = err as ApiError
      const data = apiErr.response?.data
      if (data) {
        const flat: Record<string, string> = {}
        for (const [k, v] of Object.entries(data)) {
          flat[k] = Array.isArray(v) ? v[0] : String(v)
        }
        setErrors(flat)
      } else {
        setErrors({ general: 'Error al registrar. Intenta de nuevo.' })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {/* Email */}
      <FormField label="Correo electrónico">
        <Input
          type="email"
          placeholder="tu@correo.com"
          value={form.email}
          onChange={(e) => set('email', e.target.value)}
          error={errors.email}
          required
        />
      </FormField>

      {/* Nombre + Apellido en fila */}
      <div className="grid grid-cols-2 gap-3">
        <FormField label="Nombre">
          <Input
            type="text"
            placeholder="Juan"
            value={form.nombre}
            onChange={(e) => set('nombre', e.target.value)}
            error={errors.nombre}
          />
        </FormField>
        <FormField label="Apellido">
          <Input
            type="text"
            placeholder="Pérez"
            value={form.apellido}
            onChange={(e) => set('apellido', e.target.value)}
            error={errors.apellido}
          />
        </FormField>
      </div>

      {/* Contraseña */}
      <FormField label="Contraseña">
        <Input
          type="password"
          placeholder="Crea una contraseña segura"
          value={form.password}
          onChange={(e) => set('password', e.target.value)}
          error={errors.password}
          required
        />
        <PasswordRequisitos password={form.password} />
      </FormField>

      {/* Confirmar contraseña */}
      <FormField label="Confirmar contraseña">
        <Input
          type="password"
          placeholder="Repite la contraseña"
          value={form.password_confirmar}
          onChange={(e) => set('password_confirmar', e.target.value)}
          error={errors.password_confirmar}
          required
        />
      </FormField>

      {(errors.general || errors.non_field_errors) && (
        <p className="text-sm text-red-600 text-center">
          {errors.general ?? errors.non_field_errors}
        </p>
      )}

      <Button type="submit" loading={loading} size="lg" className="w-full mt-1">
        Crear cuenta
      </Button>

      <p className="text-center text-sm text-gray-500">
        ¿Ya tienes cuenta?{' '}
        <Link to="/login" className="text-blue-600 hover:underline font-medium">
          Inicia sesión
        </Link>
      </p>
    </form>
  )
}
