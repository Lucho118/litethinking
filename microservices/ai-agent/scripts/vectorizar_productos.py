#!/usr/bin/env python
"""
Script para vectorizar todos los productos existentes en la BD.

Uso (desde el directorio microservices/ai-agent/):
    python scripts/vectorizar_productos.py

Requiere:
    - OPENAI_API_KEY en .env (o en el entorno)
    - DATABASE_URL apuntando a PostgreSQL con la extensión pgvector habilitada
    - La migración 0002_add_embedding en backend/ ya aplicada (manage.py migrate)

Cuándo ejecutar:
    1. Primera vez, después de cargar empresas y productos en el sistema.
    2. Tras una carga masiva de productos (importación CSV, etc.).
    Para actualizaciones individuales (crear/editar un producto), en el futuro
    se conectará al signal post_save de ProductoModel via webhook o Celery task.
"""

import sys
from pathlib import Path

# Asegura que el directorio raíz del microservicio esté en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from config import get_settings
from database import SessionLocal
from services.embeddings import formatear_embedding, get_embeddings_client


def main() -> None:
    settings = get_settings()

    if not settings.ia_habilitada:
        sys.exit(1)

    client = get_embeddings_client()
    db = SessionLocal()

    try:
        productos = db.execute(
            text(
                "SELECT codigo, nombre, caracteristicas, empresa_id FROM productos "
                "WHERE embedding IS NULL"
            )
        ).fetchall()

        total = len(productos)
        if total == 0:
            return

        ok = errores = 0
        for i, (codigo, nombre, caracteristicas, empresa_id) in enumerate(productos, 1):
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
                ok += 1
            except Exception as exc:
                errores += 1

        db.commit()

    except Exception as exc:
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
