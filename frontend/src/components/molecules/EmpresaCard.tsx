import { useNavigate } from 'react-router-dom'
import type { Empresa } from '@/types'

interface EmpresaCardProps {
  empresa: Empresa
}

export function EmpresaCard({ empresa }: EmpresaCardProps) {
  const navigate = useNavigate()

  return (
    <article
      onClick={() => navigate(`/empresas/${empresa.nit}`)}
      className="cursor-pointer rounded-xl border border-gray-200 bg-white p-5 shadow-sm
                 hover:shadow-md hover:border-blue-300 transition-all duration-200"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-semibold text-gray-900 text-base leading-snug">
          {empresa.nombre}
        </h3>
        <span className="shrink-0 rounded-md bg-blue-50 px-2 py-0.5 text-xs font-mono text-blue-700">
          {empresa.nit}
        </span>
      </div>
      <p className="mt-2 text-sm text-gray-500 line-clamp-2">{empresa.direccion}</p>
      <p className="mt-1 text-xs text-gray-400">{empresa.telefono}</p>
    </article>
  )
}
