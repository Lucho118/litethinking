import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { PrivateRoute } from '@/router/PrivateRoute'
import { LoginPage } from '@/pages/LoginPage'
import { RegistroPage } from '@/pages/RegistroPage'
import { EmpresasPage } from '@/pages/EmpresasPage'
import { ProductosPage } from '@/pages/ProductosPage'
import { EmpresaDetailPage } from '@/pages/EmpresaDetailPage'
import { ProductoDetailPage } from '@/pages/ProductoDetailPage'

/**
 * Organización de rutas:
 *
 * Públicas:
 *   /login          → LoginPage
 *   /registro       → RegistroPage
 *
 * Protegidas (PrivateRoute → redirige a /login si no hay sesión):
 *   /               → redirect a /empresas
 *   /empresas       → EmpresasPage      (mosaico de empresas)
 *   /productos      → ProductosPage     (mosaico de productos)
 *   /empresas/:nit  → EmpresaDetailPage (inventario + datos empresa)
 *   /productos/:codigo → ProductoDetailPage
 *
 * Decisión sobre mosaico/tabs: rutas separadas (/empresas y /productos)
 * para que el back button y los bookmarks funcionen correctamente.
 * NavbarTabs infiere el tab activo desde la URL (useLocation).
 */
export default function App() {
  const hydrate = useAuthStore((s) => s.hydrate)

  // Hidrata el estado de sesión desde localStorage al arrancar
  useEffect(() => {
    hydrate()
  }, [hydrate])

  return (
    <BrowserRouter>
      <Routes>
        {/* Públicas */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegistroPage />} />

        {/* Protegidas */}
        <Route element={<PrivateRoute />}>
          <Route path="/" element={<Navigate to="/empresas" replace />} />
          <Route path="/empresas" element={<EmpresasPage />} />
          <Route path="/empresas/:nit" element={<EmpresaDetailPage />} />
          <Route path="/productos" element={<ProductosPage />} />
          <Route path="/productos/:codigo" element={<ProductoDetailPage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
