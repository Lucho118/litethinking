import { AuthLayout } from '@/templates/AuthLayout'
import { FormularioRegistro } from '@/components/organisms/FormularioRegistro'

export function RegistroPage() {
  return (
    <AuthLayout
      title="Crear cuenta"
      subtitle="Tu cuenta tendrá acceso de lectura (rol Externo)"
    >
      <FormularioRegistro />
    </AuthLayout>
  )
}
