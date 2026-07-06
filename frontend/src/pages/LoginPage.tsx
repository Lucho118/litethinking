import { AuthLayout } from '@/templates/AuthLayout'
import { FormularioLogin } from '@/components/organisms/FormularioLogin'

export function LoginPage() {
  return (
    <AuthLayout
      title="Iniciar sesión"
      subtitle="Gestión de empresas y productos"
    >
      <FormularioLogin />
    </AuthLayout>
  )
}
