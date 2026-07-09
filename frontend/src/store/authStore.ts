/**
 * Store de autenticación con Zustand.
 *
 * Decisión: Zustand > Context API porque:
 * - No requiere envolver el árbol con Providers.
 * - Permite leer/mutar el estado desde cualquier componente sin prop drilling.
 * - El estado persiste entre rutas sin boilerplate de useReducer/useContext.
 *
 * El token se guarda en localStorage para sobrevivir recargas de página.
 * El estado en memoria (store) se hidrata al importar el módulo.
 */
import { create } from 'zustand'
import { api } from '@/lib/api'
import type { UsuarioInfo, TokenResponse } from '@/types'

interface AuthState {
  user: UsuarioInfo | null
  isAuthenticated: boolean
  isLoading: boolean

  login: (email: string, password: string) => Promise<void>
  register: (
    email: string,
    password: string,
    password_confirmar: string,
    nombre?: string,
    apellido?: string,
  ) => Promise<void>
  logout: () => void

  // Hidrata el estado desde localStorage (llamado en main.tsx al arrancar)
  hydrate: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email, password) => {
    const { data } = await api.post<TokenResponse>('/auth/login/', {
      email,
      password,
    })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(data.user))
    set({ user: data.user, isAuthenticated: true })
  },

  register: async (
    email: string,
    password: string,
    password_confirmar: string,
    nombre?: string,
    apellido?: string,
  ) => {
    // El endpoint /auth/register/ ya devuelve tokens — los usamos directamente
    const { data } = await api.post<TokenResponse>('/auth/register/', {
      email,
      password,
      password_confirmar,
      nombre: nombre ?? '',
      apellido: apellido ?? '',
    })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(data.user))
    set({ user: data.user, isAuthenticated: true })
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    set({ user: null, isAuthenticated: false })
  },

  hydrate: async () => {
    const accessToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (!accessToken || !storedUser) {
      set({ isLoading: false })
      return
    }

    // Verificar si el access token ha expirado (con 30s de margen)
    const isExpired = (token: string): boolean => {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        return Date.now() >= payload.exp * 1000 - 30_000
      } catch {
        return true
      }
    }

    const user: UsuarioInfo = JSON.parse(storedUser)

    // Token vigente → restaurar sesión directamente sin llamada al servidor
    if (!isExpired(accessToken)) {
      set({ user, isAuthenticated: true, isLoading: false })
      return
    }

    // Token expirado → intentar refrescar
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      set({ user: null, isAuthenticated: false, isLoading: false })
      return
    }

    try {
      const { data } = await api.post<{ access: string }>('/auth/refresh/', { refresh: refreshToken })
      localStorage.setItem('access_token', data.access)
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (err: any) {
      const status = err?.response?.status
      if (status === 401 || status === 403) {
        // Refresh token inválido o expirado → cerrar sesión
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        set({ user: null, isAuthenticated: false, isLoading: false })
      } else {
        // Error de red (servidor dormido, etc.) → mantener sesión
        set({ user, isAuthenticated: true, isLoading: false })
      }
    }
  },
}))

export const isAdmin = (user: UsuarioInfo | null) =>
  user?.grupos?.includes('Administrador') ?? false
