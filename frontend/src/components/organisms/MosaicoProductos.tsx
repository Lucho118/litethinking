import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { useAuthStore, isAdmin } from '@/store/authStore'
import { ProductoCard } from '@/components/molecules/ProductoCard'
import { Button } from '@/components/atoms/Button'
import type { Producto } from '@/types'

interface MosaicoProductosProps {
  empresaNit?: string  // si se pasa, filtra por empresa (vista de detalle)
}

export function MosaicoProductos({ empresaNit }: MosaicoProductosProps) {
  const [productos, setProductos] = useState<Producto[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuthStore()
  const admin = isAdmin(user)
  const navigate = useNavigate()

  useEffect(() => {
    const url = empresaNit
      ? `/productos/?empresa_nit=${empresaNit}&moneda=COP,USD,EUR`
      : '/productos/?moneda=COP,USD,EUR'

    api
      .get<Producto[]>(url)
      .then((r) => setProductos(r.data))
      .catch(() => setError('No se pudieron cargar los productos.'))
      .finally(() => setLoading(false))
  }, [empresaNit])

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
          Productos{' '}
          <span className="text-sm font-normal text-gray-400">
            ({productos.length})
          </span>
        </h2>
        {admin && (
          <Button
            size="sm"
            onClick={() =>
              navigate(`/productos/nuevo${empresaNit ? `?empresa=${empresaNit}` : ''}`)
            }
          >
            + Nuevo producto
          </Button>
        )}
      </div>

      {productos.length === 0 ? (
        <p className="text-center text-gray-400 py-10">
          Esta empresa no tiene productos registrados.
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {productos.map((p) => (
            <ProductoCard key={p.codigo} producto={p} />
          ))}
        </div>
      )}
    </section>
  )
}
