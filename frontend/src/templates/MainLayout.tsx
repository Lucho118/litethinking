import type { ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { NavbarTabs } from '@/components/organisms/NavbarTabs'
import { ChatWidget } from '@/components/organisms/ChatWidget'

interface MainLayoutProps {
  children: ReactNode
}

type Tab = 'empresas' | 'productos'

function inferTab(pathname: string): Tab {
  if (pathname.startsWith('/productos')) return 'productos'
  return 'empresas'
}

export function MainLayout({ children }: MainLayoutProps) {
  const { pathname } = useLocation()
  const activeTab = inferTab(pathname)

  return (
    <div className="min-h-screen bg-gray-50">
      <NavbarTabs activeTab={activeTab} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {children}
      </main>

      {/* Chat IA flotante — siempre visible en todas las rutas protegidas */}
      <ChatWidget />
    </div>
  )
}
