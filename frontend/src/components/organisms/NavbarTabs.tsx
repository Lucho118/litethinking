import { useNavigate } from 'react-router-dom'
import { useAuthStore, isAdmin } from '@/store/authStore'
import { Badge } from '@/components/atoms/Badge'
import { Button } from '@/components/atoms/Button'

type Tab = 'empresas' | 'productos'

interface NavbarTabsProps {
  activeTab: Tab
}

export function NavbarTabs({ activeTab }: NavbarTabsProps) {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const admin = isAdmin(user)

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-14">
        {/* Logo / Brand */}
        <button
          onClick={() => navigate('/')}
          className="font-bold text-blue-700 text-lg tracking-tight hover:opacity-80"
        >
          LiteThinking
        </button>

        {/* Tabs */}
        <nav className="flex gap-1">
          {(['empresas', 'productos'] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => navigate(`/${tab}`)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors capitalize
                ${activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              {tab}
            </button>
          ))}
        </nav>

        {/* User info + logout */}
        <div className="flex items-center gap-3">
          {user && (
            <>
              <span className="text-xs text-gray-500 hidden sm:block">{user.email}</span>
              <Badge
                label={admin ? 'Administrador' : 'Externo'}
                color={admin ? 'blue' : 'gray'}
              />
            </>
          )}
          <Button variant="ghost" size="sm" onClick={handleLogout}>
            Salir
          </Button>
        </div>
      </div>
    </header>
  )
}
