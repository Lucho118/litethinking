import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/atoms/Button'
import { Input } from '@/components/atoms/Input'
import { FormField } from '@/components/molecules/FormField'

interface ApiError {
  response?: { data?: Record<string, string[]> }
  message?: string
}

export function FormularioLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  const login = useAuthStore((s) => s.login)
  const navigate = useNavigate()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErrors({})
    setLoading(true)
    try {
      await login(email, password)
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
        setErrors({ general: 'Credenciales incorrectas' })
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
          placeholder="admin@empresa.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
          required
        />
      </FormField>

      <FormField label="Contraseña">
        <Input
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
          required
        />
      </FormField>

      {errors.general && (
        <p className="text-sm text-red-600 text-center">{errors.general}</p>
      )}
      {errors.detail && (
        <p className="text-sm text-red-600 text-center">{errors.detail}</p>
      )}

      <Button type="submit" loading={loading} size="lg" className="w-full">
        Iniciar sesión
      </Button>

      <p className="text-center text-sm text-gray-500">
        ¿No tienes cuenta?{' '}
        <Link to="/registro" className="text-blue-600 hover:underline font-medium">
          Regístrate aquí
        </Link>
      </p>
    </form>
  )
}
