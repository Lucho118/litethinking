from __future__ import annotations

from typing import Optional

from langchain_openai import OpenAIEmbeddings

from config import get_settings


def get_embeddings_client() -> Optional[OpenAIEmbeddings]:
    """Devuelve el cliente de embeddings o None si no hay API key configurada."""
    settings = get_settings()
    if not settings.ia_habilitada:
        return None
    return OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_EMBEDDING_MODEL,
    )


def embed_texto(texto: str) -> Optional[list[float]]:
    """
    Genera el embedding de un texto.
    Devuelve None si OPENAI_API_KEY no está configurada.
    """
    client = get_embeddings_client()
    if client is None:
        return None
    return client.embed_query(texto)


def formatear_embedding(vector: list[float]) -> str:
    """Convierte un vector Python a la representación string de pgvector: [0.1,0.2,...]"""
    return "[" + ",".join(str(x) for x in vector) + "]"
