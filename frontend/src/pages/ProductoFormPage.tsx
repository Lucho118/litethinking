import { useState, useEffect } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { api } from '@/lib/api'
import { MainLayout } from '@/templates/MainLayout'
import { Button } from '@/components/atoms/Button'
import { Input } from '@/components/atoms/Input'
import { FormField } from '@/components/molecules/FormField'
import type { Producto, Empresa } from '@/types'

interface ProductoForm {
  codigo: string
  nombre: string
  caracteristicas: string
  precio_monto: string
  precio_moneda: string
  empresa_nit: string
}

interface ApiError {
  response?: { data?: Record<string, string | string[]> }
}

export function ProductoFormPage() {
  const { codigo } = useParams<{ codigo: string }>()
  const [searchParams] = useSearchParams()
  const isEdit = Boolean(codigo)
  const navigate = useNavigate()

  const [form, setForm] = useState<ProductoForm>({
    codigo: '',
    nombre: '',
    caracteristicas: '',
    precio_monto: '',
    precio_moneda: 'COP',
    empresa_nit: searchParams.get('empresa') ?? '',
  })
  const [empresas, setEmpresas] = useState<Empresa[]>([])
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(isEdit)

  // Cargar empresas para el select
  useEffect(() => {
    api.get<Empresa[]>('/empresas/').then((r) => setEmpresas(r.data))
  }, [])

  // Cargar datos del producto si es edición
  useEffect(() => {
    if (!isEdit || !codigo) return
    api.get<Producto>(`/productos/${codigo}/`)
      .then((r) => {
        setForm({
          codigo: r.data.codigo,
          nombre: r.data.nombre,
          caracteristicas: r.data.caracteristicas,
          precio_monto: r.data.precio_base,
          precio_moneda: r.data.moneda_base,
          empresa_nit: r.data.empresa,
        })
      })
      .catch(() => navigate('/productos'))
      .finally(() => setLoadingData(false))
  }, [codigo, isEdit, navigate])

  function set(field: keyof ProductoForm, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: '' }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setErrors({})
    try {
      if (isEdit) {
        await api.put(`/productos/${codigo}/`, form)
      } else {
        await api.post('/productos/', form)
      }
      navigate(form.empresa_nit ? `/empresas/${form.empresa_nit}` : '/productos')
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
            {isEdit ? 'Editar producto' : 'Nuevo producto'}
          </h1>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <FormField label="Código">
              <Input
                placeholder="TCO-001"
                value={form.codigo}
                onChange={(e) => set('codigo', e.target.value)}
                error={errors.codigo}
                disabled={isEdit}
                required
              />
            </FormField>

            <FormField label="Nombre">
              <Input
                placeholder="Nombre del producto"
                value={form.nombre}
                onChange={(e) => set('nombre', e.target.value)}
                error={errors.nombre}
                required
              />
            </FormField>

            <FormField label="Características">
              <textarea
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                           shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows={4}
                placeholder="Describe las características del producto..."
                value={form.caracteristicas}
                onChange={(e) => set('caracteristicas', e.target.value)}
              />
            </FormField>

            <div className="grid grid-cols-2 gap-3">
              <FormField label="Precio">
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  value={form.precio_monto}
                  onChange={(e) => set('precio_monto', e.target.value)}
                  error={errors.precio_monto}
                  required
                />
              </FormField>

              <FormField label="Moneda">
                <select
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                             shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  value={form.precio_moneda}
                  onChange={(e) => set('precio_moneda', e.target.value)}
                >
                  <option value="COP">COP</option>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                </select>
              </FormField>
            </div>

            <FormField label="Empresa">
              <select
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                           shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                value={form.empresa_nit}
                onChange={(e) => set('empresa_nit', e.target.value)}
                required
              >
                <option value="">Selecciona una empresa...</option>
                {empresas.map((e) => (
                  <option key={e.nit} value={e.nit}>
                    {e.nombre} ({e.nit})
                  </option>
                ))}
              </select>
              {errors.empresa_nit && (
                <p className="mt-1 text-xs text-red-600">{errors.empresa_nit}</p>
              )}
            </FormField>

            {errors.general && (
              <p className="text-sm text-red-600">{errors.general}</p>
            )}

            <div className="flex gap-3 pt-2">
              <Button type="button" variant="secondary" onClick={() => navigate(-1)}>
                Cancelar
              </Button>
              <Button type="submit" loading={loading}>
                {isEdit ? 'Guardar cambios' : 'Crear producto'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </MainLayout>
  )
}
