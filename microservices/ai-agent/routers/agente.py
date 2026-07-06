from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import Settings, get_settings
from database import get_db
from services.embeddings import embed_texto, formatear_embedding
from services.rag import generar_respuesta

router = APIRouter(prefix="/agente", tags=["agente"])

_SIN_API_KEY = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail=(
        "Servicio de IA no disponible. "
        "Configure OPENAI_API_KEY en el archivo .env del microservicio."
    ),
)

# ── Schemas ───────────────────────────────────────────────────────────────────

class ConsultaRequest(BaseModel):
    pregunta: str


class ProductoContexto(BaseModel):
    codigo: str
    nombre: str
    caracteristicas: Optional[str] = ""
    precio_base: str
    moneda_base: str
    empresa_id: str


class ConsultaResponse(BaseModel):
    respuesta: str
    productos_relacionados: list[ProductoContexto]


# ── Helpers ───────────────────────────────────────────────────────────────────

_SQL_SIMILARES = text(
    """
    SELECT codigo, nombre, caracteristicas,
           precio_base::text, moneda_base, empresa_id
    FROM   productos
    WHERE  embedding IS NOT NULL
    ORDER  BY embedding <=> CAST(:emb AS vector)
    LIMIT  :top_k
    """
)


def _buscar_similares(db: Session, embedding: list[float], top_k: int) -> list[dict]:
    emb_str = formatear_embedding(embedding)
    rows = db.execute(_SQL_SIMILARES, {"emb": emb_str, "top_k": top_k}).fetchall()
    return [
        {
            "codigo":          row[0],
            "nombre":          row[1],
            "caracteristicas": row[2] or "",
            "precio_base":     row[3],
            "moneda_base":     row[4],
            "empresa_id":      row[5],
        }
        for row in rows
    ]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/consulta", response_model=ConsultaResponse)
def consultar(
    body: ConsultaRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ConsultaResponse:
    """
    Flujo RAG:
    1. Embed la pregunta del usuario.
    2. Recupera los TOP_K productos más similares (pgvector cosine distance).
    3. Construye el prompt con los productos como contexto.
    4. Llama a gpt-4o-mini via LangChain y devuelve la respuesta en lenguaje natural.
    """
    if not settings.ia_habilitada:
        raise _SIN_API_KEY

    # 1. Embedding de la pregunta
    embedding = embed_texto(body.pregunta)
    if embedding is None:
        raise _SIN_API_KEY

    # 2. Búsqueda semántica en pgvector
    productos = _buscar_similares(db, embedding, settings.TOP_K_RESULTS)

    if not productos:
        return ConsultaResponse(
            respuesta=(
                "No hay productos vectorizados todavía. "
                "Ejecuta POST /agente/reindexar para generar los embeddings."
            ),
            productos_relacionados=[],
        )

    # 3 + 4. RAG: prompt + LLM
    respuesta = generar_respuesta(body.pregunta, productos)

    return ConsultaResponse(
        respuesta=respuesta,
        productos_relacionados=[ProductoContexto(**p) for p in productos],
    )


@router.post("/reindexar", summary="Genera embeddings para todos los productos")
def reindexar(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    """
    Genera y guarda el embedding de cada producto en la columna 'embedding'.
    Ejecutar manualmente la primera vez, o tras cargas masivas de productos.

    TODO: en producción, disparar automáticamente desde el signal post_save
    de ProductoModel (via webhook Django → microservicio o Celery task).
    """
    if not settings.ia_habilitada:
        raise _SIN_API_KEY

    from services.embeddings import get_embeddings_client

    client = get_embeddings_client()
    if client is None:
        raise _SIN_API_KEY

    productos = db.execute(
        text("SELECT codigo, nombre, caracteristicas, empresa_id FROM productos")
    ).fetchall()

    actualizados = errores = 0
    for codigo, nombre, caracteristicas, empresa_id in productos:
        texto = f"{nombre}. {caracteristicas or ''}. Empresa NIT: {empresa_id}"
        try:
            emb = client.embed_query(texto)
            db.execute(
                text(
                    "UPDATE productos SET embedding = CAST(:emb AS vector) "
                    "WHERE codigo = :codigo"
                ),
                {"emb": formatear_embedding(emb), "codigo": codigo},
            )
            actualizados += 1
        except Exception as exc:  # noqa: BLE001
            errores += 1

    db.commit()
    return {
        "mensaje": "Reindexación completada",
        "actualizados": actualizados,
        "errores": errores,
    }
