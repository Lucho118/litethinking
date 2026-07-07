import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '@/lib/api'
import { MainLayout } from '@/templates/MainLayout'
import { Button } from '@/components/atoms/Button'
import { Input } from '@/components/atoms/Input'
import { FormField } from '@/components/molecules/FormField'
import type { Empresa } from '@/types'

interface ApiError {
  response?: { data?: Record<string, string | string[]> }
}

export function EmpresaFormPage() {
  const { nit } = useParams<{ nit: string }>()
  const isEdit = Boolean(nit)
  const navigate = useNavigate()

  const [form, setForm] = useState({ nit: '', nombre: '', direccion: '', telefono: '' })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(isEdit)

  useEffect(() => {
    if (!isEdit || !nit) return
    api.get<Empresa>(`/empresas/${nit}/`)
      .then((r) => setForm(r.data))
      .catch(() => navigate('/empresas'))
      .finally(() => setLoadingData(false))
  }, [nit, isEdit, navigate])

  function set(field: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: '' }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setErrors({})
    try {
      if (isEdit) {
        await api.put(`/empresas/${nit}/`, form)
      } else {
        await api.post('/empresas/', form)
      }
      navigate(isEdit ? `/empresas/${nit}` : '/empresas')
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
        setErrors({ general: 'Error al guardar. Intenta de nuevo.' })
      }
    } finally {
      setLoading(false)
    }
  }

  if (loadingData) {
    return (
      <MainLayout>
        <div className="flex justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        </div>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <div className="max-w-lg mx-auto">
        <button onClick={() => navigate(-1)} className="text-sm text-blue-600 hover:underline mb-4 flex items-center gap-1">
          ← Volver
        </button>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
          <h1 className="text-xl font-bold text-gray-900 mb-6">
            {isEdit ? 'Editar empresa' : 'Nueva empresa'}
          </h1>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <FormField label="NIT">
              <Input
                placeholder="900123456-1"
                value={form.nit}
                onChange={(e) => set('nit', e.target.value)}
                error={errors.nit}
                disabled={isEdit}
                required
              />
            </FormField>

            <FormField label="Nombre">
              <Input
                placeholder="Nombre de la empresa"
                value={form.nombre}
                onChange={(e) => set('nombre', e.target.value)}
                error={errors.nombre}
                required
              />
            </FormField>

            <FormField label="Dirección">
              <Input
                placeholder="Cra 7 # 32-16, Bogotá"
                value={form.direccion}
                onChange={(e) => set('direccion', e.target.value)}
                error={errors.direccion}
                required
              />
            </FormField>

            <FormField label="Teléfono">
              <Input
                placeholder="+57 300 123 4567"
                value={form.telefono}
                onChange={(e) => set('telefono', e.target.value)}
                error={errors.telefono}
                required
              />
            </FormField>

            {errors.general && (
              <p className="text-sm text-red-600">{errors.general}</p>
            )}

            <div className="flex gap-3 pt-2">
              <Button type="button" variant="secondary" onClick={() => navigate(-1)}>
                Cancelar
              </Button>
              <Button type="submit" loading={loading}>
                {isEdit ? 'Guardar cambios' : 'Crear empresa'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </MainLayout>
  )
}
