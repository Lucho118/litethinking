import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { useAuthStore, isAdmin } from '@/store/authStore'
import { EmpresaCard } from '@/components/molecules/EmpresaCard'
import { Button } from '@/components/atoms/Button'
import type { Empresa } from '@/types'

export function MosaicoEmpresas() {
  const [empresas, setEmpresas] = useState<Empresa[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuthStore()
  const admin = isAdmin(user)
  const navigate = useNavigate()

  useEffect(() => {
    api
      .get<Empresa[]>('/empresas/')
      .then((r) => setEmpresas(r.data))
      .catch(() => setError('No se pudieron cargar las empresas.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading)
    return (
      <div className="flex justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    )

  if (error)
    return <p className="text-center text-red-500 py-10">{error}</p>

  return (
    <section>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">
          Empresas{' '}
          <span className="text-sm font-normal text-gray-400">
            ({empresas.length})
          </span>
        </h2>
        {admin && (
          <Button size="sm" onClick={() => navigate('/empresas/nueva')}>
            + Nueva empresa
          </Button>
        )}
      </div>

      {empresas.length === 0 ? (
        <p className="text-center text-gray-400 py-16">No hay empresas registradas.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {empresas.map((e) => (
            <EmpresaCard key={e.nit} empresa={e} />
          ))}
        </div>
      )}
    </section>
  )
}
