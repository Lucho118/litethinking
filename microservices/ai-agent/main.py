from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.agente import router as agente_router

app = FastAPI(
    title="AI Agent — RAG sobre catálogo de productos",
    description=(
        "Microservicio independiente que responde preguntas en lenguaje natural "
        "sobre el catálogo de productos usando búsqueda semántica (pgvector) y "
        "LangChain + OpenAI GPT-4o-mini."
    ),
    version="0.1.0",
)

# CORS: permite peticiones desde el frontend React en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://litethinking.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agente_router)


@app.get("/health")
async def health() -> dict:
    from config import get_settings
    settings = get_settings()
    return {
        "status": "ok",
        "ia_habilitada": settings.ia_habilitada,
        "embedding_model": settings.OPENAI_EMBEDDING_MODEL,
        "chat_model": settings.OPENAI_CHAT_MODEL,
    }
