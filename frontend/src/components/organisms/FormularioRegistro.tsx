import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/atoms/Button'
import { Input } from '@/components/atoms/Input'
import { FormField } from '@/components/molecules/FormField'

interface ApiError {
  response?: { data?: Record<string, string[]> }
}

// Reglas de contraseña (espejo del backend FuertePasswordValidator)
function validarPassword(pwd: string): string | null {
  if (pwd.length < 8) return 'Mínimo 8 caracteres'
  if (!/[A-Z]/.test(pwd)) return 'Debe contener al menos una mayúscula'
  if (!/\d/.test(pwd)) return 'Debe contener al menos un número'
  if (!/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(pwd))
    return 'Debe contener al menos un carácter especial'
  return null
}

export function FormularioRegistro() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  const register = useAuthStore((s) => s.register)
  const navigate = useNavigate()

  function validate(): boolean {
    const newErrors: Record<string, string> = {}
    if (!email) newErrors.email = 'El correo es requerido'
    const pwdError = validarPassword(password)
    if (pwdError) newErrors.password = pwdError
    if (password !== confirmPassword)
      newErrors.confirmPassword = 'Las contraseñas no coinciden'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      await register(email, password)
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
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      <FormField label="Correo electrónico">
        <Input
          type="email"
          placeholder="tu@correo.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
          required
        />
      </FormField>

      <FormField label="Contraseña">
        <Input
          type="password"
          placeholder="Mín. 8 chars, mayúscula, número, especial"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
          required
        />
      </FormField>

      <FormField label="Confirmar contraseña">
        <Input
          type="password"
          placeholder="Repite la contraseña"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          error={errors.confirmPassword}
          required
        />
      </FormField>

      {(errors.general || errors.non_field_errors) && (
        <p className="text-sm text-red-600 text-center">
          {errors.general ?? errors.non_field_errors}
        </p>
      )}

      <Button type="submit" loading={loading} size="lg" className="w-full">
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
