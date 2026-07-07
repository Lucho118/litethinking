# Arquitectura del proyecto

## Clean Architecture aplicada

El proyecto aplica los principios de Arquitectura Limpia con cuatro capas bien definidas. La regla fundamental es la **dirección de las dependencias**: las capas externas pueden depender de las internas, nunca al revés.

```
┌─────────────────────────────────────────────────────────────────┐
│  Presentación          frontend/  (React, Vite, TypeScript)     │
├─────────────────────────────────────────────────────────────────┤
│  Aplicación +          backend/   (Django, DRF, PostgreSQL ORM) │
│  Infraestructura       microservices/ai-agent/  (FastAPI, pgvector) │
├─────────────────────────────────────────────────────────────────┤
│  Dominio               domain/    (Python puro, sin frameworks) │
└─────────────────────────────────────────────────────────────────┘
         Las dependencias solo apuntan hacia ABAJO (→ dominio)
```

### Diagrama de dependencias

```
frontend/  ──────────────────────────────────────►  (sin dep Python)
                                                      │
backend/   ──────────────►  domain/                   │
                ↑                                      │
microservices/ ai-agent/ ──►  domain/                 │
                                                      │
PostgreSQL  ◄──  backend/  ◄──────────────────────────┘
PostgreSQL  ◄──  microservices/ai-agent/
```

**Quién puede importar a quién:**

| Capa | Puede importar | Prohibido importar |
|---|---|---|
| `domain/` | nada externo (solo stdlib) | Django, FastAPI, SQLAlchemy, DRF |
| `backend/` | `domain/`, Django, DRF | FastAPI, módulos de `microservices/` |
| `microservices/ai-agent/` | `domain/`, FastAPI, SQLAlchemy | Django, módulos de `backend/` |
| `frontend/` | React, axios, recharts | nada del lado servidor |

---

## Por qué `domain/` es un paquete Poetry independiente

`domain/` tiene su propio `pyproject.toml` y se instala como *path dependency* desde `backend/` y desde `microservices/ai-agent/`:

```toml
# en backend/pyproject.toml y microservices/ai-agent/pyproject.toml
domain = {path = "../domain", develop = true}
```

Ventajas:
1. **Zero-framework:** Al no importar Django ni FastAPI, las entidades son testables en microsegundos sin levantar ningún servidor.
2. **Cambio sin duplicación:** Si se renombra un campo en `Producto`, el cambio se propaga a ambas capas en el próximo `poetry install`.
3. **Despliegue independiente:** Un microservicio nuevo puede consumir `domain/` sin copiar código.

---

## Patrón por entidad

Cada vez que se agrega una entidad nueva, se sigue este orden estricto:

```
1. domain/domain/entities/<entidad>.py       ← dataclass puro, sin imports de framework
2. backend/apps/<feature>/models.py          ← modelo ORM (separado de la entidad)
3. backend/apps/<feature>/repositories.py   ← traduce ORM ↔ entidad
4. backend/apps/<feature>/use_cases.py      ← lógica de aplicación, llama al repositorio
5. backend/apps/<feature>/serializers.py    ← validación y serialización DRF
6. backend/apps/<feature>/views.py          ← HTTP, delega en use_case
7. backend/apps/<feature>/urls.py           ← enrutamiento
```

Las **vistas y serializers nunca acceden directamente a `domain/`** — siempre pasan por `repositories/use_cases`.

---

## ADR-001 — Separación de capas (Clean Architecture)

**Fecha:** 2026-07-06 | **Estado:** Vigente

**Decisión:** Aplicar Arquitectura Limpia con domain como paquete independiente y cada capa en su propia carpeta Poetry/npm.

**Consecuencias:**
- Las entidades de dominio se pueden testear sin Django overhead.
- Intercambiar el framework de persistencia (ej. Django → SQLAlchemy) solo afecta `backend/`, no el dominio.
- Cada microservicio es independientemente desplegable.

---

## ADR-002 — Frontend: Atomic Design

**Fecha:** 2026-07-06 | **Estado:** Vigente

**Decisión:** `frontend/src/components/` se organiza en tres niveles:
- `atoms/` — UI primitiva sin lógica de negocio (Button, Input, Badge).
- `molecules/` — composiciones de átomos (FormField, Card).
- `organisms/` — bloques de feature con estado local o hooks (MosaicoEmpresas, ChatWidget).

Pages en `frontend/src/pages/`. Rutas en `frontend/src/App.tsx` + `PrivateRoute`.

