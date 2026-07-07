import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { NavbarTabs } from '@/components/organisms/NavbarTabs'
import { useAuthStore, isAdmin } from '@/store/authStore'
import { api } from '@/lib/api'
import type { DashboardResumen } from '@/types'

// ── Componente auxiliar: Card de métrica ─────────────────────────────────────

interface MetricCardProps {
  label: string
  value: number | string
  color?: string
}

function MetricCard({ label, value, color = 'blue' }: MetricCardProps) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
    orange: 'bg-orange-50 border-orange-200 text-orange-700',
  }
  return (
    <div className={`rounded-xl border p-5 flex flex-col gap-1 ${colors[color] ?? colors.blue}`}>
      <span className="text-sm font-medium opacity-70">{label}</span>
      <span className="text-3xl font-bold">{value}</span>
    </div>
  )
}

// ── Página principal ──────────────────────────────────────────────────────────

export function DashboardPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [resumen, setResumen] = useState<DashboardResumen | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // Protección de ruta: si el usuario no es Administrador, denegar acceso
  if (!isAdmin(user)) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavbarTabs activeTab="dashboard" />
        <main className="max-w-2xl mx-auto px-4 py-20 text-center">
          <p className="text-2xl font-bold text-red-600 mb-2">Acceso denegado</p>
          <p className="text-gray-500">Esta sección es exclusiva para Administradores.</p>
          <button
            onClick={() => navigate('/empresas')}
            className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm"
          >
            Volver al inicio
          </button>
        </main>
      </div>
    )
  }

  useEffect(() => {
    api
      .get<DashboardResumen>('/dashboard/resumen/')
      .then((r) => setResumen(r.data))
      .catch(() => setError('Error al cargar el dashboard. Intenta de nuevo.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    )
  }

  if (error || !resumen) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NavbarTabs activeTab="dashboard" />
        <main className="max-w-2xl mx-auto px-4 py-20 text-center">
          <p className="text-red-500">{error ?? 'Sin datos disponibles.'}</p>
        </main>
      </div>
    )
  }

  const COLORES_BARRA = ['#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#ec4899']

  return (
    <div className="min-h-screen bg-gray-50">
      <NavbarTabs activeTab="dashboard" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-10">
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>

        {/* ── Cards de totales ── */}
        <section className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <MetricCard label="Empresas" value={resumen.total_empresas} color="blue" />
          <MetricCard label="Productos" value={resumen.total_productos} color="green" />
          <MetricCard label="Registros de auditoría" value={resumen.total_auditoria} color="purple" />
          <MetricCard
            label="Producto más consultado"
            value={resumen.producto_mas_consultado?.nombre ?? '—'}
            color="orange"
          />
        </section>

        {/* ── Producto más consultado (card detalle) ── */}
        {resumen.producto_mas_consultado && (
          <section>
            <h2 className="text-lg font-semibold text-gray-700 mb-3">Producto más consultado en el chat</h2>
            <div className="bg-white rounded-xl border border-yellow-200 p-5 flex items-center gap-6 shadow-sm max-w-sm">
              <div className="text-4xl">🏆</div>
              <div>
                <p className="text-base font-bold text-gray-800">{resumen.producto_mas_consultado.nombre}</p>
                <p className="text-sm text-gray-500">Código: {resumen.producto_mas_consultado.codigo}</p>
                <p className="text-sm font-medium text-yellow-700 mt-1">
                  {resumen.producto_mas_consultado.total_consultas} consultas
                </p>
              </div>
            </div>
          </section>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* ── Top 5 empresas ── */}
          <section>
            <h2 className="text-lg font-semibold text-gray-700 mb-3">Top 5 empresas con más productos</h2>
            <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
              {resumen.top_5_empresas.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-8">Sin datos</p>
              ) : (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart
                    data={resumen.top_5_empresas}
                    margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis
                      dataKey="nombre"
                      tick={{ fontSize: 11 }}
                      tickFormatter={(v: string) => (v.length > 12 ? v.slice(0, 12) + '…' : v)}
                    />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip
                      formatter={(value) => [value, 'Productos']}
                      labelFormatter={(label) => `Empresa: ${label}`}
                    />
                    <Bar dataKey="cantidad_productos" radius={[4, 4, 0, 0]}>
                      {resumen.top_5_empresas.map((_, i) => (
                        <Cell key={i} fill={COLORES_BARRA[i % COLORES_BARRA.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </section>

          {/* ── Distribución por precio ── */}
          <section>
            <h2 className="text-lg font-semibold text-gray-700 mb-3">Distribución de productos por precio</h2>
            <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
              {resumen.distribucion_precios.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-8">Sin datos</p>
              ) : (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart
                    data={resumen.distribucion_precios}
                    margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="rango" tick={{ fontSize: 11 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip
                      formatter={(value) => [value, 'Productos']}
                      labelFormatter={(label) => `Rango: ${label}`}
                    />
                    <Bar dataKey="cantidad" radius={[4, 4, 0, 0]}>
                      <Cell fill="#10b981" />
                      <Cell fill="#3b82f6" />
                      <Cell fill="#8b5cf6" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}
