from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import Settings, get_settings
from database import get_db
from services.cache import respuesta_cache
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
    precios_convertidos: dict[str, float] = {}


class ConsultaResponse(BaseModel):
    respuesta: str
    productos_relacionados: list[ProductoContexto]
    from_cache: bool = False


# ── Helpers ───────────────────────────────────────────────────────────────────

_SQL_REGISTRAR_CONSULTA = text(
    """
    INSERT INTO consultas_productos (codigo, total_consultas)
    VALUES (:codigo, 1)
    ON CONFLICT (codigo)
    DO UPDATE SET total_consultas = consultas_productos.total_consultas + 1
    """
)


def _registrar_consultas(db: Session, productos: list[dict]) -> None:
    """Incrementa el contador de consultas por cada producto aparecido en la respuesta."""
    for p in productos:
        try:
            db.execute(_SQL_REGISTRAR_CONSULTA, {"codigo": p["codigo"]})
        except Exception:  # noqa: BLE001 — no queremos que un fallo de estadísticas rompa el flujo
            pass
    try:
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()


_SQL_SIMILARES = text(
    """
    SELECT p.codigo, p.nombre, p.caracteristicas,
           p.precio_base::text, p.moneda_base, p.empresa_id
    FROM   productos p
    WHERE  p.embedding IS NOT NULL
    ORDER  BY p.embedding <=> CAST(:emb AS vector)
    LIMIT  :top_k
    """
)

_SQL_TASAS = text(
    """
    SELECT moneda_origen, moneda_destino, tasa::float
    FROM   tasas_cambio
    """
)


def _cargar_tasas(db: Session) -> dict[tuple[str, str], float]:
    """Carga todas las tasas de cambio en un dict para conversión rápida."""
    rows = db.execute(_SQL_TASAS).fetchall()
    return {(r[0], r[1]): r[2] for r in rows}


def _convertir_precios(
    precio_base: float,
    moneda_base: str,
    tasas: dict[tuple[str, str], float],
    monedas_destino: list[str] = ["COP", "USD", "EUR"],
) -> dict[str, float]:
    resultado: dict[str, float] = {}
    for destino in monedas_destino:
        if destino == moneda_base:
            resultado[destino] = round(precio_base, 2)
        elif (moneda_base, destino) in tasas:
            resultado[destino] = round(precio_base * tasas[(moneda_base, destino)], 2)
    return resultado


def _buscar_similares(db: Session, embedding: list[float], top_k: int) -> list[dict]:
    emb_str = formatear_embedding(embedding)
    rows = db.execute(_SQL_SIMILARES, {"emb": emb_str, "top_k": top_k}).fetchall()
    tasas = _cargar_tasas(db)
    productos = []
    for row in rows:
        precio_float = float(row[3])
        moneda_base = row[4]
        precios_convertidos = _convertir_precios(precio_float, moneda_base, tasas)
        productos.append({
            "codigo":              row[0],
            "nombre":              row[1],
            "caracteristicas":     row[2] or "",
            "precio_base":         row[3],
            "moneda_base":         moneda_base,
            "empresa_id":          row[5],
            "precios_convertidos": precios_convertidos,
        })
    return productos


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

    # ── Cache hit ──────────────────────────────────────────────────────────
    entrada_cache = respuesta_cache.obtener(body.pregunta)
    if entrada_cache is not None:
        # Registrar consultas aunque la respuesta venga de cache
        _registrar_consultas(db, entrada_cache["productos"])
        return ConsultaResponse(
            respuesta=entrada_cache["respuesta"],
            productos_relacionados=[
                ProductoContexto(**p) for p in entrada_cache["productos"]
            ],
            from_cache=True,
        )

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

    # ── Guardar en cache y registrar consultas ─────────────────────────────
    respuesta_cache.guardar(body.pregunta, {"respuesta": respuesta, "productos": productos})
    _registrar_consultas(db, productos)

    return ConsultaResponse(
        respuesta=respuesta,
        productos_relacionados=[ProductoContexto(**p) for p in productos],
        from_cache=False,
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


@router.post("/reindexar/{codigo}", summary="Vectoriza un producto específico e invalida el cache")
def reindexar_uno(
    codigo: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    """
    Genera el embedding de un producto específico e invalida el cache del agente.
    Llamado automáticamente desde el signal post_save de Django al crear/editar un producto.
    """
    if not settings.ia_habilitada:
        raise _SIN_API_KEY

    from services.embeddings import get_embeddings_client

    client = get_embeddings_client()
    if client is None:
        raise _SIN_API_KEY

    row = db.execute(
        text("SELECT codigo, nombre, caracteristicas, empresa_id FROM productos WHERE codigo = :codigo"),
        {"codigo": codigo},
    ).fetchone()

    if row is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Producto '{codigo}' no encontrado.")

    _, nombre, caracteristicas, empresa_id = row
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
        db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        return {"mensaje": "Error al vectorizar", "codigo": codigo, "error": str(exc)}

    # Invalidar cache: el catálogo cambió, las respuestas cacheadas son obsoletas
    respuesta_cache.invalidad_todo()

    return {"mensaje": "Producto vectorizado y cache invalidado", "codigo": codigo}
