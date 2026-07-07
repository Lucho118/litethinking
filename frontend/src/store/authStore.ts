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
    set({ user: data.user, isAuthenticated: true })
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, isAuthenticated: false })
  },

  hydrate: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ isLoading: false })
      return
    }
    try {
      // Usamos el endpoint de refresh para verificar la sesión y obtener info del usuario
      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) throw new Error('no refresh')
      const { data } = await api.post<{ access: string }>('/auth/refresh/', {
        refresh,
      })
      localStorage.setItem('access_token', data.access)

      // Decodifica el payload del JWT para obtener info básica del usuario
      // (sin llamada extra al backend)
      const payload = JSON.parse(atob(data.access.split('.')[1]))
      const user: UsuarioInfo = {
        id: payload.user_id,
        email: payload.email ?? '',
        grupos: payload.grupos ?? [],
      }
      set({ user, isAuthenticated: true, isLoading: false })
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },
}))

export const isAdmin = (user: UsuarioInfo | null) =>
  user?.grupos?.includes('Administrador') ?? false
