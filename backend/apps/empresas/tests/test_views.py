import pytest
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_client(db, django_user_model):
    group, _ = Group.objects.get_or_create(name="Administrador")
    user = django_user_model.objects.create_user(username="admin_test", password="pass123!")
    user.groups.add(group)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


EMPRESA_PAYLOAD = {
    "nit": "830514226-6",
    "nombre": "Acme S.A.S.",
    "direccion": "Calle 1 # 2-3, Bogotá",
    "telefono": "3001234567",
}


# ── Tests: permisos ───────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_listar_empresas_es_publico(api_client):
    response = api_client.get("/api/empresas/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.django_db
def test_crear_empresa_sin_autenticacion_retorna_401_o_403(api_client):
    """Con JWT activo, unauthenticated = 401; authenticated sin permiso = 403."""
    payload = {
        "nit": "830514226-6",
        "nombre": "Acme S.A.S.",
        "direccion": "Calle 1 #2-3",
        "telefono": "3001234567",
    }
    response = api_client.post("/api/empresas/", payload, format="json")
    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


# ── Tests: CRUD completo como Administrador ───────────────────────────────────

@pytest.mark.django_db
def test_crear_empresa(admin_client):
    response = admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["nit"] == EMPRESA_PAYLOAD["nit"]


@pytest.mark.django_db
def test_crear_empresa_nit_duplicado_retorna_400(admin_client):
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    response = admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_crear_empresa_nit_invalido_retorna_400(admin_client):
    payload = {**EMPRESA_PAYLOAD, "nit": "INVALIDO"}
    response = admin_client.post("/api/empresas/", payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "nit" in response.json()


@pytest.mark.django_db
def test_obtener_empresa(admin_client):
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    response = admin_client.get(f"/api/empresas/{EMPRESA_PAYLOAD['nit']}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nombre"] == EMPRESA_PAYLOAD["nombre"]


@pytest.mark.django_db
def test_obtener_empresa_inexistente_retorna_404(api_client):
    response = api_client.get("/api/empresas/000000000-0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_actualizar_empresa(admin_client):
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    payload_actualizado = {**EMPRESA_PAYLOAD, "nombre": "Acme Corp S.A.S."}
    response = admin_client.put(
        f"/api/empresas/{EMPRESA_PAYLOAD['nit']}/",
        payload_actualizado,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nombre"] == "Acme Corp S.A.S."


@pytest.mark.django_db
def test_eliminar_empresa(admin_client):
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    response = admin_client.delete(f"/api/empresas/{EMPRESA_PAYLOAD['nit']}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's gone
    response = admin_client.get(f"/api/empresas/{EMPRESA_PAYLOAD['nit']}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_eliminar_empresa_inexistente_retorna_404(admin_client):
    response = admin_client.delete("/api/empresas/000000000-0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
