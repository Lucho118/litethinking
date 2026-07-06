import pytest
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from apps.auditoria.models import BloqueAuditoriaModel
from apps.empresas.models import EmpresaModel


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def grupos(db):
    Group.objects.get_or_create(name="Administrador")
    Group.objects.get_or_create(name="Externo")


@pytest.fixture
def admin_client(db, django_user_model, grupos):
    user = django_user_model.objects.create_user(
        username="admin_audit@test.com",
        email="admin_audit@test.com",
        password="Admin123!",
    )
    user.groups.add(Group.objects.get(name="Administrador"))
    client = APIClient()
    client.force_authenticate(user=user)
    return client


EMPRESA_PAYLOAD = {
    "nit": "830514226-6",
    "nombre": "Acme S.A.S.",
    "direccion": "Calle 1 #2-3",
    "telefono": "3001234567",
}


# ── Signals: generación automática de bloques ─────────────────────────────────

@pytest.mark.django_db
def test_crear_empresa_genera_bloque_auditoria(admin_client):
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")

    assert BloqueAuditoriaModel.objects.count() == 1
    bloque = BloqueAuditoriaModel.objects.first()
    assert bloque.entidad == "Empresa"
    assert bloque.accion == "CREAR"
    assert bloque.entidad_id == EMPRESA_PAYLOAD["nit"]
    assert bloque.indice == 0
    assert bloque.hash_anterior == "0" * 64   # bloque génesis


@pytest.mark.django_db
def test_editar_empresa_genera_bloque_editar(admin_client):
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    admin_client.put(
        f"/api/empresas/{EMPRESA_PAYLOAD['nit']}/",
        {**EMPRESA_PAYLOAD, "nombre": "Acme Corp"},
        format="json",
    )

    assert BloqueAuditoriaModel.objects.filter(accion="EDITAR").count() == 1
    bloque_editar = BloqueAuditoriaModel.objects.get(accion="EDITAR")
    assert bloque_editar.indice == 1    # segundo bloque


@pytest.mark.django_db
def test_eliminar_empresa_genera_bloque_eliminar(admin_client):
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    admin_client.delete(f"/api/empresas/{EMPRESA_PAYLOAD['nit']}/")

    assert BloqueAuditoriaModel.objects.filter(accion="ELIMINAR").count() == 1


@pytest.mark.django_db
def test_hash_encadenado_correctamente(admin_client):
    """Cada bloque tiene hash_anterior == hash_actual del bloque previo."""
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    admin_client.put(
        f"/api/empresas/{EMPRESA_PAYLOAD['nit']}/",
        {**EMPRESA_PAYLOAD, "nombre": "Acme Corp"},
        format="json",
    )

    b0 = BloqueAuditoriaModel.objects.get(indice=0)
    b1 = BloqueAuditoriaModel.objects.get(indice=1)
    assert b1.hash_anterior == b0.hash_actual


# ── Endpoints ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_listar_auditoria_requiere_admin(api_client, admin_client):
    response = api_client.get("/api/auditoria/")
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_listar_auditoria_devuelve_bloques(admin_client):
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")

    response = admin_client.get("/api/auditoria/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["count"] == 1
    bloque = data["results"][0]
    assert bloque["entidad"] == "Empresa"
    assert "hash_actual" in bloque
    assert "hash_anterior" in bloque


# ── Verificar integridad ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_cadena_integra_retorna_200(admin_client):
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")

    response = admin_client.get("/api/auditoria/verificar/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["integra"] is True
    assert data["total_bloques"] == 1
    assert data["ruptura_en_indice"] is None


@pytest.mark.django_db
def test_cadena_vacia_es_integra(admin_client):
    response = admin_client.get("/api/auditoria/verificar/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["integra"] is True


@pytest.mark.django_db
def test_cadena_manipulada_detecta_ruptura(admin_client):
    """
    Altera directamente el campo 'datos' en BD (simulando un ataque).
    verificar_integridad() debe detectar la ruptura en el índice 0.
    """
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")

    # Manipulación directa en BD — no pasa por los use cases
    BloqueAuditoriaModel.objects.filter(indice=0).update(
        datos={"manipulado": True, "nit": "000000000-0"}
    )

    response = admin_client.get("/api/auditoria/verificar/")
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert data["integra"] is False
    assert data["ruptura_en_indice"] == 0


@pytest.mark.django_db
def test_ruptura_detectada_en_bloque_correcto(admin_client):
    """Crea 3 bloques, manipula el del medio — la ruptura se detecta en índice 1."""
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    admin_client.put(
        f"/api/empresas/{EMPRESA_PAYLOAD['nit']}/",
        {**EMPRESA_PAYLOAD, "nombre": "Acme Corp"},
        format="json",
    )
    admin_client.put(
        f"/api/empresas/{EMPRESA_PAYLOAD['nit']}/",
        {**EMPRESA_PAYLOAD, "nombre": "Acme Final"},
        format="json",
    )

    BloqueAuditoriaModel.objects.filter(indice=1).update(datos={"tampered": True})

    response = admin_client.get("/api/auditoria/verificar/")
    data = response.json()
    assert data["integra"] is False
    assert data["ruptura_en_indice"] == 1


# ── Historial por entidad ─────────────────────────────────────────────────────

@pytest.mark.django_db
def test_historial_entidad_empresa(admin_client):
    admin_client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    admin_client.put(
        f"/api/empresas/{EMPRESA_PAYLOAD['nit']}/",
        {**EMPRESA_PAYLOAD, "nombre": "Acme Corp"},
        format="json",
    )

    response = admin_client.get(f"/api/auditoria/entidad/Empresa/{EMPRESA_PAYLOAD['nit']}/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["accion"] == "CREAR"
    assert data[1]["accion"] == "EDITAR"


@pytest.mark.django_db
def test_historial_entidad_sin_registros(admin_client):
    response = admin_client.get("/api/auditoria/entidad/Empresa/000000000-0/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
