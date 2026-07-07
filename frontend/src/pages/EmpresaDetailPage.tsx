import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { useAuthStore, isAdmin } from '@/store/authStore'
import { MainLayout } from '@/templates/MainLayout'
import { MosaicoProductos } from '@/components/organisms/MosaicoProductos'
import { Button } from '@/components/atoms/Button'
import { Input } from '@/components/atoms/Input'
import type { Empresa } from '@/types'

export function EmpresaDetailPage() {
  const { nit } = useParams<{ nit: string }>()
  const [empresa, setEmpresa] = useState<Empresa | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [emailInput, setEmailInput] = useState('')
  const [emailLoading, setEmailLoading] = useState(false)
  const [emailMsg, setEmailMsg] = useState<{ ok: boolean; text: string } | null>(null)
  const [pdfLoading, setPdfLoading] = useState(false)
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

  async function handleDescargarPDF() {
    if (!nit) return
    setPdfLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/api/empresas/${nit}/inventario/pdf/`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      if (!response.ok) throw new Error('Error al generar PDF')
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `inventario_${nit.replace('-', '_')}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      alert('No se pudo descargar el inventario.')
    } finally {
      setPdfLoading(false)
    }
  }

  async function handleEnviarEmail() {
    if (!nit || !emailInput.trim()) return
    setEmailLoading(true)
    setEmailMsg(null)
    try {
      await api.post(`/empresas/${nit}/inventario/email/`, { email: emailInput.trim() })
      setEmailMsg({ ok: true, text: `Inventario enviado a ${emailInput.trim()}` })
      setEmailInput('')
    } catch {
      setEmailMsg({ ok: false, text: 'No se pudo enviar. Verifica la configuración de email.' })
    } finally {
      setEmailLoading(false)
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

        <div className="flex flex-col gap-2 shrink-0">
          {/* Acciones admin */}
          {admin && (
            <div className="flex gap-2">
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

          {/* Inventario PDF */}
          <Button
            variant="secondary"
            size="sm"
            loading={pdfLoading}
            onClick={handleDescargarPDF}
          >
            ⬇ Descargar inventario PDF
          </Button>

          {/* Inventario por email */}
          <div className="flex gap-2">
            <Input
              type="email"
              placeholder="correo@ejemplo.com"
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleEnviarEmail()}
              className="text-sm"
            />
            <Button
              variant="primary"
              size="sm"
              loading={emailLoading}
              disabled={!emailInput.trim()}
              onClick={handleEnviarEmail}
            >
              ✉ Enviar
            </Button>
          </div>
          {emailMsg && (
            <p className={`text-xs ${emailMsg.ok ? 'text-green-600' : 'text-red-500'}`}>
              {emailMsg.text}
            </p>
          )}
        </div>
      </div>

      {/* Productos de esta empresa */}
      <MosaicoProductos empresaNit={nit} />
    </MainLayout>
  )
}
