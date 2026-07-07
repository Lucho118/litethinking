# Despliegue

## Render (configuración actual)

El proyecto incluye `render.yaml` en la raíz — Render lo detecta automáticamente al conectar el repositorio y crea los dos servicios web de una vez (**Blueprint deploy**).

### Pasos

1. En [render.com](https://render.com), ir a **New → Blueprint** y conectar el repositorio.
2. Render detecta `render.yaml` y propone crear los dos servicios.
3. Antes de confirmar, rellenar las variables marcadas como `[REQUIRED]`:

#### `litethinking-backend` (Django)

| Variable | Cómo obtenerla |
|---|---|
| `SECRET_KEY` | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `ALLOWED_HOSTS` | dominio asignado por Render, ej. `litethinking-backend.onrender.com` |
| `DATABASE_URL` | URL de la PostgreSQL de Render / Supabase / Neon |
| `CORS_ALLOWED_ORIGINS` | URL del frontend, ej. `https://litethinking.vercel.app` |
| `AI_AGENT_URL` | URL del microservicio ai-agent en Render (disponible tras desplegarlo) |

#### `litethinking-ai-agent` (FastAPI)

| Variable | Cómo obtenerla |
|---|---|
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| `DATABASE_URL` | misma que el backend |

4. Después del primer deploy, ejecutar una vez desde el shell de Render:
   ```bash
   # En el shell del servicio backend:
   python manage.py crear_admin --email admin@empresa.com --password "Admin123!"
   
   # En el shell del servicio ai-agent (tras crear productos desde el frontend):
   curl -X POST https://litethinking-ai-agent.onrender.com/agente/reindexar
   ```

5. Habilitar `pgvector` en la BD (una sola vez):
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

---

## Variables de entorno por componente

### `backend/` (Django)

| Variable | Descripción | Requerida |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django | Sí |
| `DEBUG` | `False` en producción | Sí |
| `DATABASE_URL` | URL completa de PostgreSQL | Sí |
| `CORS_ALLOWED_ORIGINS` | URL del frontend desplegado | Sí |
| `AI_AGENT_URL` | URL del microservicio ai-agent desplegado | Sí |
| `EMAIL_HOST_USER` | Correo Gmail para envío de inventarios | Opcional |
| `EMAIL_HOST_PASSWORD` | App Password de Gmail | Opcional |
| `DEFAULT_FROM_EMAIL` | Remitente visible en emails | Opcional |

### `microservices/ai-agent/` (FastAPI)

| Variable | Descripción | Requerida |
|---|---|---|
| `OPENAI_API_KEY` | API key de OpenAI | Sí (para chat IA) |
| `DATABASE_URL` | URL completa de PostgreSQL (misma que backend) | Sí |
| `OPENAI_EMBEDDING_MODEL` | Modelo de embeddings (`text-embedding-3-small`) | No (tiene default) |
| `OPENAI_CHAT_MODEL` | Modelo de chat (`gpt-4o-mini`) | No (tiene default) |
| `TOP_K_RESULTS` | Productos a recuperar por consulta (default: 5) | No |

### `frontend/` (React/Vite)

| Variable | Descripción | Requerida |
|---|---|---|
| `VITE_API_BASE_URL` | URL del backend Django desplegado | Sí en producción |
| `VITE_AI_AGENT_URL` | URL del microservicio ai-agent desplegado | Sí en producción |

---

## Checklist de despliegue

### Base de datos

- [ ] Provisionar PostgreSQL 15+ (Supabase, Neon, Railway, RDS, etc.)
- [ ] Habilitar extensión: `CREATE EXTENSION IF NOT EXISTS vector;`
- [ ] Obtener `DATABASE_URL` en formato `postgresql://user:pass@host:5432/db`

### Backend Django (Render / Railway / Fly.io)

- [ ] Configurar variables de entorno listadas arriba
- [ ] Build command: `poetry install --no-dev`
- [ ] Start command: `poetry run gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
- [ ] Ejecutar migraciones: `poetry run python manage.py migrate`
- [ ] Crear admin: `poetry run python manage.py crear_admin --email X --password Y`
- [ ] Configurar `ALLOWED_HOSTS` con el dominio asignado
- [ ] Configurar `CORS_ALLOWED_ORIGINS` con la URL del frontend

### Microservicio IA (Render / Railway)

- [ ] Configurar variables de entorno (especialmente `OPENAI_API_KEY` y `DATABASE_URL`)
- [ ] Start command: `poetry run uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Vectorizar catálogo inicial: `POST /agente/reindexar`

### Frontend (Vercel / Netlify)

- [ ] Configurar `VITE_API_BASE_URL` con la URL del backend desplegado
- [ ] Configurar `VITE_AI_AGENT_URL` con la URL del microservicio desplegado
- [ ] Build command: `npm run build`
- [ ] Output directory: `dist`
- [ ] Configurar rewrite rule: `/* → /index.html` (para React Router)

---

## Notas de seguridad para producción

- Nunca commitear archivos `.env` con valores reales (están en `.gitignore`).
- `SECRET_KEY` debe ser un valor aleatorio de al menos 50 caracteres.
- `DEBUG=False` es obligatorio en producción.
- La `OPENAI_API_KEY` debe tener límites de uso configurados en el dashboard de OpenAI.
- Revisar que `CORS_ALLOWED_ORIGINS` no incluya `*` en producción.
