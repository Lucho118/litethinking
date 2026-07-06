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
    user = django_user_model.objects.create_user(
        username="admin_inv@test.com", email="admin_inv@test.com", password="Admin123!"
    )
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


PRODUCTO_PAYLOAD = {
    "codigo": "PROD-001",
    "nombre": "Laptop X1",
    "caracteristicas": "16GB RAM, 512GB SSD",
    "precio_monto": "2500000.00",
    "precio_moneda": "COP",
    "empresa_nit": "830514226-6",
}


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_inventario_empresa_sin_productos(api_client, empresa):
    """Empresa existente pero sin productos → lista vacía, no error."""
    response = api_client.get(f"/api/empresas/{empresa.nit}/inventario/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["empresa"]["nit"] == empresa.nit
    assert data["empresa"]["nombre"] == "Acme S.A.S."
    assert data["total_productos"] == 0
    assert data["productos"] == []


@pytest.mark.django_db
def test_inventario_empresa_con_productos(api_client, admin_client, empresa, tasas):
    """Devuelve los productos de la empresa con datos completos y precios convertidos."""
    admin_client.post("/api/productos/", PRODUCTO_PAYLOAD, format="json")

    response = api_client.get(f"/api/empresas/{empresa.nit}/inventario/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["empresa"]["nit"] == empresa.nit
    assert data["total_productos"] == 1

    producto = data["productos"][0]
    assert producto["codigo"] == "PROD-001"
    assert producto["nombre"] == "Laptop X1"
    assert "precio_base" in producto
    assert producto["precio_base"]["moneda"] == "COP"
    assert "precios" in producto
    assert "USD" in producto["precios"]
    assert "EUR" in producto["precios"]


@pytest.mark.django_db
def test_inventario_solo_devuelve_productos_de_esa_empresa(
    api_client, admin_client, empresa, tasas, db, django_user_model
):
    """Los productos de otras empresas no aparecen en el inventario."""
    otra = EmpresaModel.objects.create(
        nit="900111222-3", nombre="Beta Corp", direccion="Av 2", telefono="311"
    )
    admin_client.post("/api/productos/", PRODUCTO_PAYLOAD, format="json")
    admin_client.post(
        "/api/productos/",
        {**PRODUCTO_PAYLOAD, "codigo": "PROD-002", "empresa_nit": otra.nit},
        format="json",
    )

    response = api_client.get(f"/api/empresas/{empresa.nit}/inventario/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_productos"] == 1
    assert data["productos"][0]["codigo"] == "PROD-001"


@pytest.mark.django_db
def test_inventario_empresa_inexistente_retorna_404(api_client):
    """NIT que no existe en la BD → 404 claro con mensaje de error."""
    response = api_client.get("/api/empresas/000000000-0/inventario/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in response.json()


@pytest.mark.django_db
def test_inventario_es_publico_sin_autenticar(api_client, empresa):
    """El inventario es de solo lectura: cualquiera puede consultarlo."""
    response = api_client.get(f"/api/empresas/{empresa.nit}/inventario/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_inventario_incluye_datos_de_empresa(api_client, empresa):
    """La respuesta incluye todos los campos de la empresa (no solo el NIT)."""
    response = api_client.get(f"/api/empresas/{empresa.nit}/inventario/")
    data = response.json()
    emp = data["empresa"]
    assert emp["nit"] == empresa.nit
    assert emp["nombre"] == empresa.nombre
    assert emp["direccion"] == empresa.direccion
    assert emp["telefono"] == empresa.telefono
