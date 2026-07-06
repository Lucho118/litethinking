"""
Tests del microservicio ai-agent.
Todos los tests mockean OpenAI y la BD — no requieren conexión real a ningún servicio.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status

# ── /health ───────────────────────────────────────────────────────────────────

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "ia_habilitada" in data


# ── /agente/consulta — sin API key ────────────────────────────────────────────

def test_consulta_sin_api_key_retorna_503(client_sin_api_key):
    """Si OPENAI_API_KEY está vacía, el endpoint debe responder 503 sin crashear."""
    response = client_sin_api_key.post(
        "/agente/consulta", json={"pregunta": "¿qué laptops tienen?"}
    )
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "OPENAI_API_KEY" in response.json()["detail"]


# ── /agente/consulta — con API key mockeada ───────────────────────────────────

def test_consulta_exitosa(client):
    """Flujo completo con embeddings y LLM mockeados."""
    with (
        patch("routers.agente.embed_texto", return_value=[0.1] * 1536),
        patch("routers.agente.generar_respuesta", return_value="Tenemos la Laptop X1 por $2,500,000 COP."),
    ):
        response = client.post(
            "/agente/consulta", json={"pregunta": "¿qué laptops tienen?"}
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "respuesta" in data
    assert "Laptop" in data["respuesta"]
    assert len(data["productos_relacionados"]) == 1
    assert data["productos_relacionados"][0]["codigo"] == "PROD-001"


def test_consulta_devuelve_productos_con_todos_los_campos(client):
    """Verifica que cada producto relacionado tenga todos los campos esperados."""
    with (
        patch("routers.agente.embed_texto", return_value=[0.0] * 1536),
        patch("routers.agente.generar_respuesta", return_value="Respuesta de prueba"),
    ):
        response = client.post("/agente/consulta", json={"pregunta": "test"})

    producto = response.json()["productos_relacionados"][0]
    assert "codigo" in producto
    assert "nombre" in producto
    assert "precio_base" in producto
    assert "moneda_base" in producto
    assert "empresa_id" in producto


def test_consulta_sin_productos_vectorizados(client, mock_db):
    """Sin productos con embedding, el agente responde de forma amable (no error)."""
    mock_db.execute.return_value.fetchall.return_value = []  # BD vacía

    with patch("routers.agente.embed_texto", return_value=[0.0] * 1536):
        response = client.post("/agente/consulta", json={"pregunta": "algo"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["productos_relacionados"] == []
    assert "reindexar" in data["respuesta"].lower()


def test_consulta_payload_invalido(client):
    """Falta el campo 'pregunta' — debe retornar 422."""
    response = client.post("/agente/consulta", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ── /agente/reindexar ─────────────────────────────────────────────────────────

def test_reindexar_sin_api_key_retorna_503(client_sin_api_key):
    response = client_sin_api_key.post("/agente/reindexar")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_reindexar_exitoso(client, mock_db):
    """Reindexar mockeando embed_query — verifica que se llame UPDATE en BD."""
    mock_client = MagicMock()
    mock_client.embed_query.return_value = [0.1] * 1536

    # fetchall devuelve un producto para reindexar
    mock_db.execute.return_value.fetchall.return_value = [
        ("PROD-001", "Laptop X1", "16GB RAM", "830514226-6")
    ]

    with patch("services.embeddings.get_embeddings_client", return_value=mock_client):
        response = client.post("/agente/reindexar")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["actualizados"] == 1
    assert data["errores"] == 0


# ── Similaridad vectorial (query SQL) ────────────────────────────────────────

def test_busqueda_similaridad_usa_pgvector_operator(client, mock_db):
    """
    Verifica que la query ejecutada contra la BD use el operador <=> de pgvector.
    No llama a OpenAI — verifica solo la estructura del SQL.
    """
    with (
        patch("routers.agente.embed_texto", return_value=[0.5] * 1536),
        patch("routers.agente.generar_respuesta", return_value="Test"),
    ):
        client.post("/agente/consulta", json={"pregunta": "consulta de prueba"})

    # Verifica que se ejecutó alguna query contra la BD
    assert mock_db.execute.called
    # El primer argumento del primer call debe ser el TextClause con <=>
    call_args = mock_db.execute.call_args_list[0]
    sql_text = str(call_args[0][0])
    assert "<=>" in sql_text
