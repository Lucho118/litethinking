from decimal import Decimal

import pytest
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from apps.empresas.models import EmpresaModel
from apps.productos.models import TasaCambioModel


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_client(db, django_user_model):
    group, _ = Group.objects.get_or_create(name="Administrador")
    user = django_user_model.objects.create_user(username="admin_prod", password="pass123!")
    user.groups.add(group)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def empresa(db):
    return EmpresaModel.objects.create(
        nit="830514226-6",
        nombre="Acme S.A.S.",
        direccion="Calle 1 #2-3",
        telefono="3001234567",
    )


@pytest.fixture
def tasas(db):
    TasaCambioModel.objects.create(
        moneda_origen="COP", moneda_destino="USD", tasa=Decimal("0.00024000")
    )
    TasaCambioModel.objects.create(
        moneda_origen="COP", moneda_destino="EUR", tasa=Decimal("0.00022000")
    )


def _payload(empresa_nit="830514226-6"):
    return {
        "codigo": "PROD-001",
        "nombre": "Laptop X1",
        "caracteristicas": "16GB RAM, 512GB SSD",
        "precio_monto": "2500000.00",
        "precio_moneda": "COP",
        "empresa_nit": empresa_nit,
    }


# ── Permisos ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_listar_productos_es_publico(api_client):
    response = api_client.get("/api/productos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.django_db
def test_crear_producto_sin_autenticacion_retorna_401_o_403(api_client, empresa):
    """Con JWT activo, unauthenticated = 401; authenticated sin permiso = 403."""
    response = api_client.post("/api/productos/", _payload(), format="json")
    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


# ── CRUD como Administrador ───────────────────────────────────────────────────

@pytest.mark.django_db
def test_crear_producto(admin_client, empresa, tasas):
    response = admin_client.post("/api/productos/", _payload(), format="json")
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["codigo"] == "PROD-001"
    assert data["empresa_nombre"] == "Acme S.A.S."
    assert "precios" in data
    assert "USD" in data["precios"]
    assert "EUR" in data["precios"]


@pytest.mark.django_db
def test_crear_producto_empresa_inexistente_retorna_400(admin_client):
    response = admin_client.post("/api/productos/", _payload("000000000-0"), format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "empresa" in response.json()["error"].lower()


@pytest.mark.django_db
def test_crear_producto_codigo_duplicado_retorna_400(admin_client, empresa):
    admin_client.post("/api/productos/", _payload(), format="json")
    response = admin_client.post("/api/productos/", _payload(), format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_crear_producto_precio_negativo_retorna_400(admin_client, empresa):
    payload = {**_payload(), "precio_monto": "-100.00"}
    response = admin_client.post("/api/productos/", payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_obtener_producto_con_precios(api_client, admin_client, empresa, tasas):
    admin_client.post("/api/productos/", _payload(), format="json")
    response = api_client.get("/api/productos/PROD-001/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["precios"]["COP"]["moneda"] == "COP"
    assert data["precios"]["USD"]["moneda"] == "USD"


@pytest.mark.django_db
def test_obtener_producto_filtrar_moneda(api_client, admin_client, empresa, tasas):
    admin_client.post("/api/productos/", _payload(), format="json")
    response = api_client.get("/api/productos/PROD-001/?moneda=USD")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "USD" in data["precios"]
    assert "EUR" not in data["precios"]


@pytest.mark.django_db
def test_obtener_producto_inexistente_retorna_404(api_client):
    response = api_client.get("/api/productos/NO-EXISTE/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_actualizar_producto(admin_client, empresa, tasas):
    admin_client.post("/api/productos/", _payload(), format="json")
    payload = {**_payload(), "nombre": "Laptop X2 Pro"}
    response = admin_client.put("/api/productos/PROD-001/", payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nombre"] == "Laptop X2 Pro"


@pytest.mark.django_db
def test_eliminar_producto(admin_client, empresa):
    admin_client.post("/api/productos/", _payload(), format="json")
    response = admin_client.delete("/api/productos/PROD-001/")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = admin_client.get("/api/productos/PROD-001/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_eliminar_producto_inexistente_retorna_404(admin_client):
    response = admin_client.delete("/api/productos/NO-EXISTE/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ── Endpoint por empresa ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_listar_por_empresa(api_client, admin_client, empresa, tasas):
    admin_client.post("/api/productos/", _payload(), format="json")
    response = api_client.get(f"/api/productos/por-empresa/{empresa.nit}/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["empresa_nit"] == empresa.nit


@pytest.mark.django_db
def test_listar_por_empresa_sin_productos(api_client, empresa):
    response = api_client.get(f"/api/productos/por-empresa/{empresa.nit}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
