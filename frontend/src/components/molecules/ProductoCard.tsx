import { useNavigate } from 'react-router-dom'
import type { Producto } from '@/types'

interface ProductoCardProps {
  producto: Producto
  compact?: boolean
}

function formatPrecio(monto: string, moneda: string) {
  const num = parseFloat(monto)
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: moneda,
    minimumFractionDigits: 0,
  }).format(num)
}

export function ProductoCard({ producto, compact = false }: ProductoCardProps) {
  const navigate = useNavigate()

  const precioDisplay = producto.precios?.COP
    ? formatPrecio(producto.precios.COP.monto, 'COP')
    : formatPrecio(producto.precio_base.monto, producto.precio_base.moneda)

  return (
    <article
      onClick={() => navigate(`/productos/${producto.codigo}`)}
      className="cursor-pointer rounded-xl border border-gray-200 bg-white p-5 shadow-sm
                 hover:shadow-md hover:border-blue-300 transition-all duration-200"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-semibold text-gray-900 text-base leading-snug">
          {producto.nombre}
        </h3>
        <span className="shrink-0 rounded-md bg-gray-100 px-2 py-0.5 text-xs font-mono text-gray-600">
          {producto.codigo}
        </span>
      </div>

      {!compact && (
        <p className="mt-2 text-sm text-gray-500 line-clamp-2">
          {producto.caracteristicas}
        </p>
      )}

      <div className="mt-3 flex items-center justify-between">
        <p className="text-lg font-bold text-blue-700">{precioDisplay}</p>
        <div className="text-right">
          <p className="text-xs text-gray-500">{producto.empresa_nombre}</p>
          <p className="text-xs text-gray-400 font-mono">{producto.empresa_nit}</p>
        </div>
      </div>
    </article>
  )
}
