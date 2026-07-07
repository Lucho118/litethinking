// ─── Entidades de dominio (espejo del backend) ───────────────────────────────

export interface Empresa {
  nit: string
  nombre: string
  direccion: string
  telefono: string
}

export interface Precio {
  monto: string
  moneda: string
}

export interface Precios {
  COP?: Precio
  USD?: Precio
  EUR?: Precio
}

export interface Producto {
  codigo: string
  nombre: string
  caracteristicas: string
  cantidad: number
  precio_base: { monto: string; moneda: string }
  moneda_base: string
  empresa_nit: string
  empresa_nombre: string
  precios?: Precios
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface UsuarioInfo {
  id: number
  email: string
  grupos: string[]
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export interface TopEmpresa {
  nombre: string
  nit: string
  cantidad_productos: number
}

export interface ProductoMasConsultado {
  codigo: string
  nombre: string
  total_consultas: number
}

export interface RangoPrecio {
  rango: string
  cantidad: number
}

export interface DashboardResumen {
  total_empresas: number
  total_productos: number
  top_5_empresas: TopEmpresa[]
  producto_mas_consultado: ProductoMasConsultado | null
  distribucion_precios: RangoPrecio[]
  total_auditoria: number
}

export interface TokenResponse {
  access: string
  refresh: string
  user: UsuarioInfo
}

// ─── Inventario ───────────────────────────────────────────────────────────────

export interface Inventario {
  empresa: Empresa
  total_productos: number
  productos: Producto[]
}

// ─── Agente IA ────────────────────────────────────────────────────────────────

export interface ConsultaAgente {
  pregunta: string
}

export interface RespuestaAgente {
  respuesta: string
  productos_relacionados: Producto[]
}

// ─── Paginación DRF ───────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
