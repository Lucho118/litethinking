"""
conftest.py — configura el entorno de tests antes de importar la app FastAPI.
Pone variables de entorno mínimas para que pydantic-settings no falle
al intentar leer un .env inexistente en CI.
"""

import os

# Setear ANTES de que se importe cualquier módulo del microservicio
os.environ.setdefault("OPENAI_API_KEY", "sk-test-placeholder")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Importar después de setear las env vars
from config import get_settings, Settings
from database import get_db
from main import app


@pytest.fixture
def mock_db():
    """Sesión de BD mockeada — no requiere PostgreSQL real."""
    session = MagicMock()
    # fetchall devuelve una fila de producto de ejemplo
    row = (
        "PROD-001",
        "Laptop X1",
        "16GB RAM, 512GB SSD",
        "2500000",
        "COP",
        "830514226-6",
    )
    session.execute.return_value.fetchall.return_value = [row]
    return session


@pytest.fixture
def client(mock_db):
    """Cliente de test con BD y settings mockeados."""
    def override_db():
        yield mock_db

    def override_settings():
        return Settings(
            OPENAI_API_KEY="sk-test-placeholder",
            DATABASE_URL="postgresql://test:test@localhost/test",
        )

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = override_settings

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_sin_api_key(mock_db):
    """Cliente de test con API key vacía — simula servicio no configurado."""
    def override_db():
        yield mock_db

    def override_settings():
        return Settings(
            OPENAI_API_KEY="",
            DATABASE_URL="postgresql://test:test@localhost/test",
        )

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = override_settings

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
