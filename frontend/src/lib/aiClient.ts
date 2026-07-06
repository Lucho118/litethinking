/**
 * Cliente HTTP para el microservicio FastAPI (agente IA).
 * Separado de api.ts porque apunta a un puerto diferente y no necesita JWT.
 */
import axios from 'axios'

const AI_URL = import.meta.env.VITE_AI_AGENT_URL ?? 'http://localhost:8001'

export const aiClient = axios.create({
  baseURL: AI_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000, // el LLM puede tardar
})
