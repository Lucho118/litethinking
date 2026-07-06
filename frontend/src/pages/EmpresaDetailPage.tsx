import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { useAuthStore, isAdmin } from '@/store/authStore'
import { MainLayout } from '@/templates/MainLayout'
import { MosaicoProductos } from '@/components/organisms/MosaicoProductos'
import { Button } from '@/components/atoms/Button'
import type { Empresa } from '@/types'

export function EmpresaDetailPage() {
  const { nit } = useParams<{ nit: string }>()
  const [empresa, setEmpresa] = useState<Empresa | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuthStore()
  const admin = isAdmin(user)
  const navigate = useNavigate()

  useEffect(() => {
    if (!nit) return
    api
      .get<Empresa>(`/empresas/${nit}/`)
      .then((r) => setEmpresa(r.data))
      .catch(() => setError('Empresa no encontrada.'))
      .finally(() => setLoading(false))
  }, [nit])

  async function handleEliminar() {
    if (!nit || !confirm('¿Eliminar esta empresa? Esta acción no se puede deshacer.')) return
    try {
      await api.delete(`/empresas/${nit}/`)
      navigate('/empresas')
    } catch {
      alert('No se pudo eliminar. Verifica que no tenga productos asociados.')
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

  if (error || !empresa)
    return (
      <MainLayout>
        <p className="text-center text-red-500 py-16">{error ?? 'Error desconocido'}</p>
      </MainLayout>
    )

  return (
    <MainLayout>
      {/* Header empresa */}
      <div className="mb-8 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <button
            onClick={() => navigate('/empresas')}
            className="text-sm text-blue-600 hover:underline mb-2 flex items-center gap-1"
          >
            ← Volver a empresas
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{empresa.nombre}</h1>
          <p className="text-sm text-gray-500 mt-1 font-mono">NIT: {empresa.nit}</p>
          <p className="text-sm text-gray-500">{empresa.direccion}</p>
          <p className="text-sm text-gray-400">{empresa.telefono}</p>
        </div>

        {admin && (
          <div className="flex gap-2 shrink-0">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => navigate(`/empresas/${nit}/editar`)}
            >
              Editar
            </Button>
            <Button variant="danger" size="sm" onClick={handleEliminar}>
              Eliminar
            </Button>
          </div>
        )}
      </div>

      {/* Productos de esta empresa */}
      <MosaicoProductos empresaNit={nit} />
    </MainLayout>
  )
}
