import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { useAuthStore, isAdmin } from '@/store/authStore'
import { MainLayout } from '@/templates/MainLayout'
import { Button } from '@/components/atoms/Button'
import { Badge } from '@/components/atoms/Badge'
import type { Producto } from '@/types'

function formatPrecio(monto: string, moneda: string) {
  const num = parseFloat(monto)
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: moneda,
    minimumFractionDigits: 2,
  }).format(num)
}

const MONEDA_COLORS: Record<string, 'blue' | 'green' | 'yellow'> = {
  COP: 'blue',
  USD: 'green',
  EUR: 'yellow',
}

export function ProductoDetailPage() {
  const { codigo } = useParams<{ codigo: string }>()
  const [producto, setProducto] = useState<Producto | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuthStore()
  const admin = isAdmin(user)
  const navigate = useNavigate()

  useEffect(() => {
    if (!codigo) return
    api
      .get<Producto>(`/productos/${codigo}/?moneda=COP,USD,EUR`)
      .then((r) => setProducto(r.data))
      .catch(() => setError('Producto no encontrado.'))
      .finally(() => setLoading(false))
  }, [codigo])

  async function handleEliminar() {
    if (!codigo || !confirm('¿Eliminar este producto?')) return
    try {
      await api.delete(`/productos/${codigo}/`)
      navigate(-1)
    } catch {
      alert('No se pudo eliminar el producto.')
    }
  }

  if (loading)
    return (
      <MainLayout>
        <div className="flex justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        </div>
      </MainLayout>
    )

  if (error || !producto)
    return (
      <MainLayout>
        <p className="text-center text-red-500 py-16">{error ?? 'Error desconocido'}</p>
      </MainLayout>
    )

  return (
    <MainLayout>
      <div className="max-w-2xl mx-auto">
        {/* Breadcrumb */}
        <div className="flex gap-2 text-sm text-blue-600 mb-4">
          <button onClick={() => navigate('/empresas')} className="hover:underline">
            Empresas
          </button>
          <span className="text-gray-400">/</span>
          <button
            onClick={() => navigate(`/empresas/${producto.empresa}`)}
            className="hover:underline"
          >
            {producto.empresa}
          </button>
          <span className="text-gray-400">/</span>
          <span className="text-gray-500">{producto.codigo}</span>
        </div>

        {/* Card detalle */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
          <div className="flex items-start justify-between gap-4 mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{producto.nombre}</h1>
              <span className="inline-block mt-1 font-mono text-sm text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                {producto.codigo}
              </span>
            </div>

            {admin && (
              <div className="flex gap-2 shrink-0">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => navigate(`/productos/${codigo}/editar`)}
                >
                  Editar
                </Button>
                <Button variant="danger" size="sm" onClick={handleEliminar}>
                  Eliminar
                </Button>
              </div>
            )}
          </div>

          {/* Características */}
          {producto.caracteristicas && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Características
              </h3>
              <p className="text-gray-700 leading-relaxed">{producto.caracteristicas}</p>
            </div>
          )}

          {/* Precios */}
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Precios
            </h3>
            <div className="flex flex-wrap gap-3">
              {producto.precios
                ? Object.entries(producto.precios).map(([moneda, precio]) => (
                    <div
                      key={moneda}
                      className="flex flex-col items-center gap-1 rounded-xl border border-gray-100 bg-gray-50 px-5 py-3"
                    >
                      <Badge
                        label={moneda}
                        color={MONEDA_COLORS[moneda] ?? 'gray'}
                      />
                      <span className="text-lg font-bold text-gray-800">
                        {formatPrecio(precio.monto, moneda)}
                      </span>
                    </div>
                  ))
                : (
                  <p className="text-lg font-bold text-blue-700">
                    {formatPrecio(producto.precio_base, producto.moneda_base)}
                  </p>
                )}
            </div>
          </div>

          {/* Empresa */}
          <div className="mt-6 pt-5 border-t border-gray-100">
            <span className="text-sm text-gray-500">Empresa: </span>
            <button
              onClick={() => navigate(`/empresas/${producto.empresa}`)}
              className="text-sm text-blue-600 hover:underline font-medium"
            >
              {producto.empresa}
            </button>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
