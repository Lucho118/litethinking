# Architecture Decision Records

## ADR-001 — Clean Architecture layer separation

**Date:** 2026-07-06  
**Status:** Active

### Context
Full-stack technical challenge requiring Django, FastAPI, React/Next.js and PostgreSQL.

### Decision
Apply Clean Architecture with strict layer separation:

| Layer | Folder | Responsibility |
|---|---|---|
| Domain | `domain/` | Pure business entities (dataclasses). Zero framework deps. |
| Application + Infrastructure | `backend/` | Django ORM models, repositories, use cases, DRF serializers/views. |
| Independent microservice | `microservices/ai-agent/` | FastAPI RAG service with pgvector. |
| Presentation | `frontend/` | Next.js + Atomic Design. |

### `domain/` is a standalone Poetry package
- Installed as a local path dependency (`{path = "../domain", develop = true}`) from `backend/` and from each microservice.
- Never copied — always referenced by path so changes propagate instantly.

### Pattern per entity (to be followed every time)
```
entity in domain/domain/entities/  →  ORM model in backend/apps/<feature>/models.py
→  repository in repositories.py  →  use case in use_cases.py
→  serializer + view + urls in backend/apps/<feature>/
```

### Consequences
- `domain/` entities can be unit-tested with zero framework overhead.
- Swapping Django for another framework only touches `backend/`; domain stays intact.
- Each FastAPI microservice is independently deployable.

---

## ADR-002 — Frontend: Atomic Design

**Date:** 2026-07-06  
**Status:** Active

### Decision
`frontend/components/` is organized in three tiers:
- `atoms/` — primitive UI elements with no business logic (Button, Input, Label).
- `molecules/` — compositions of atoms (FormField, Card).
- `organisms/` — full feature blocks that may hold local state or call hooks (FormularioEmpresa, TablaProductos).

Pages live in `frontend/app/` (Next.js App Router).
