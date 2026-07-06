from fastapi import FastAPI

app = FastAPI(
    title="AI Agent",
    description="RAG microservice using pgvector",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# Routes will be registered here as features are added
