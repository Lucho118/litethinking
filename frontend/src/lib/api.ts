/**
 * Cliente HTTP centralizado para el backend Django.
 *
 * Responsabilidades:
 * - Adjunta automáticamente el Bearer token en cada request.
 * - Intenta refrescar el access token con el refresh token cuando recibe 401.
 * - Si el refresh falla (token expirado), limpia la sesión y redirige a /login.
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
})

// ─── Request interceptor: adjunta access token ────────────────────────────────
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const url = config.url ?? ''
  // No adjuntar token en endpoints públicos de autenticación
  if (url.includes('/auth/login') || url.includes('/auth/register')) {
    return config
  }

  const token = localStorage.getItem('access_token')
  if (token && config.headers) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// ─── Response interceptor: refresca el token cuando expira ───────────────────
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (err: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach((p) => (error ? p.reject(error) : p.resolve(token!)))
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    // Evitar refrescar en la propia llamada de login/refresh
    const url = originalRequest.url ?? ''
    if (url.includes('/auth/login') || url.includes('/auth/refresh')) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      }).then((token) => {
        if (originalRequest.headers) {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
        }
        return api(originalRequest)
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    const refresh = localStorage.getItem('refresh_token')
    if (!refresh) {
      clearSession()
      return Promise.reject(error)
    }

    try {
      const { data } = await axios.post(`${BASE_URL}/api/auth/refresh/`, {
        refresh,
      })
      const newAccess: string = data.access
      localStorage.setItem('access_token', newAccess)
      processQueue(null, newAccess)
      if (originalRequest.headers) {
        originalRequest.headers['Authorization'] = `Bearer ${newAccess}`
      }
      return api(originalRequest)
    } catch (refreshError) {
      processQueue(refreshError, null)
      clearSession()
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

function clearSession() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  window.location.href = '/login'
}
