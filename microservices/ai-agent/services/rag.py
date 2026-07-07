from __future__ import annotations

from typing import Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config import get_settings

# Prompt que convierte los productos recuperados en una respuesta en lenguaje natural.
# Los productos son el "contexto" del patrón RAG (Retrieval-Augmented Generation).
_PROMPT = ChatPromptTemplate.from_template(
    """Eres un asistente experto en el catálogo de productos de nuestras empresas.
Responde la pregunta del usuario basándote ÚNICAMENTE en los productos listados abajo.
Si la respuesta no está en los productos disponibles, dilo claramente en español.
Cuando menciones un producto, SIEMPRE incluye su precio (en todas las monedas disponibles).
Sé conciso y útil.

Productos disponibles:
{contexto}

Pregunta del usuario: {pregunta}

Respuesta en español:"""
)


def _construir_contexto(productos: list[dict]) -> str:
    partes = []
    for p in productos:
        # Precios: siempre incluir el precio base; convertidos si están disponibles
        precios_str = f"{p['precio_base']} {p['moneda_base']}"
        precios_extra = p.get("precios_convertidos") or {}
        if precios_extra:
            conversiones = ", ".join(
                f"{v:.2f} {m}" for m, v in sorted(precios_extra.items())
            )
            precios_str += f" (equivale a: {conversiones})"

        partes.append(
            f"• [{p['codigo']}] {p['nombre']}\n"
            f"  Características: {p.get('caracteristicas') or 'N/A'}\n"
            f"  Precio: {precios_str}\n"
            f"  Empresa (NIT): {p['empresa_id']}"
        )
    return "\n\n".join(partes)


def get_llm() -> Optional[ChatOpenAI]:
    settings = get_settings()
    if not settings.ia_habilitada:
        return None
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_CHAT_MODEL,
        temperature=0,      # respuestas deterministas para un catálogo
        max_tokens=512,     # limita costo por llamada
    )


def generar_respuesta(pregunta: str, productos_contexto: list[dict]) -> str:
    """
    Orquesta el pipeline LangChain:  prompt → LLM → string.
    Recibe los productos ya recuperados por similaridad vectorial (RAG step 2).
    """
    llm = get_llm()
    if llm is None:
        raise RuntimeError("LLM no configurado: OPENAI_API_KEY está vacía.")

    chain = _PROMPT | llm | StrOutputParser()
    return chain.invoke(
        {
            "contexto": _construir_contexto(productos_contexto),
            "pregunta": pregunta,
        }
    )
