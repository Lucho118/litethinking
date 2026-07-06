from fastapi import FastAPI

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
