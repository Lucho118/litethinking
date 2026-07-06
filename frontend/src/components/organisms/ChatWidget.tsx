import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { aiClient } from '@/lib/aiClient'
import { ChatBubble } from '@/components/molecules/ChatBubble'
import { Button } from '@/components/atoms/Button'
import { Input } from '@/components/atoms/Input'
import type { RespuestaAgente, Producto } from '@/types'

interface Message {
  role: 'user' | 'assistant'
  content: string
  productos?: Producto[]
}

export function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '¡Hola! Soy el asistente IA. Puedo ayudarte a encontrar productos. ¿En qué te puedo ayudar?',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend() {
    const pregunta = input.trim()
    if (!pregunta || loading) return

    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: pregunta }])
    setLoading(true)

    try {
      const { data } = await aiClient.post<RespuestaAgente>('/agente/consulta', {
        pregunta,
      })
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.respuesta,
          productos: data.productos_relacionados,
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'El asistente no está disponible en este momento. Intenta más tarde.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Botón flotante */}
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Abrir asistente IA"
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center
                   rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700
                   transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {open ? (
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-3 3-3-3z" />
          </svg>
        )}
      </button>

      {/* Panel de chat */}
      {open && (
        <div
          className="fixed bottom-24 right-6 z-50 flex flex-col
                     w-80 sm:w-96 h-[480px] rounded-2xl bg-white shadow-2xl border border-gray-200
                     overflow-hidden"
        >
          {/* Header */}
          <div className="bg-blue-600 px-4 py-3 flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
            <h3 className="text-white font-semibold text-sm">Asistente IA</h3>
            <span className="text-blue-200 text-xs ml-auto">Catálogo de productos</span>
          </div>

          {/* Mensajes */}
          <div className="flex-1 overflow-y-auto px-4 py-3 flex flex-col gap-3">
            {messages.map((msg, i) => (
              <div key={i}>
                <ChatBubble role={msg.role} content={msg.content} />
                {msg.productos && msg.productos.length > 0 && (
                  <div className="mt-2 flex flex-col gap-1.5 pl-2">
                    {msg.productos.map((p) => (
                      <button
                        key={p.codigo}
                        onClick={() => {
                          navigate(`/productos/${p.codigo}`)
                          setOpen(false)
                        }}
                        className="text-left rounded-lg border border-blue-100 bg-blue-50
                                   px-3 py-2 text-xs hover:bg-blue-100 transition-colors"
                      >
                        <span className="font-medium text-blue-800">{p.nombre}</span>
                        <span className="block text-blue-500">{p.codigo}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && <ChatBubble role="assistant" content="" isLoading />}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-100 px-3 py-3 flex gap-2">
            <Input
              placeholder="Escribe tu pregunta..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              disabled={loading}
              className="text-sm"
            />
            <Button
              size="sm"
              onClick={handleSend}
              loading={loading}
              disabled={!input.trim()}
              className="shrink-0"
            >
              Enviar
            </Button>
          </div>
        </div>
      )}
    </>
  )
}
