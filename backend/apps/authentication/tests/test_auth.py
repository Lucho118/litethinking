import pytest
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from apps.empresas.models import EmpresaModel


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def grupos(db):
    """Los grupos se crean vía migración; este fixture los garantiza en tests."""
    Group.objects.get_or_create(name="Administrador")
    Group.objects.get_or_create(name="Externo")


@pytest.fixture
def usuario_admin(db, django_user_model, grupos):
    user = django_user_model.objects.create_user(
        username="admin@test.com", email="admin@test.com", password="Admin123!"
    )
    user.groups.add(Group.objects.get(name="Administrador"))
    return user


@pytest.fixture
def usuario_externo(db, django_user_model, grupos):
    user = django_user_model.objects.create_user(
        username="externo@test.com", email="externo@test.com", password="Externo123!"
    )
    user.groups.add(Group.objects.get(name="Externo"))
    return user


EMPRESA_PAYLOAD = {
    "nit": "830514226-6",
    "nombre": "Acme S.A.S.",
    "direccion": "Calle 1 #2-3",
    "telefono": "3001234567",
}


# ── Login ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_login_exitoso(client, usuario_admin):
    response = client.post(
        "/api/auth/login/",
        {"email": "admin@test.com", "password": "Admin123!"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access" in data
    assert "refresh" in data
    assert data["user"]["email"] == "admin@test.com"
    assert "Administrador" in data["user"]["grupos"]


@pytest.mark.django_db
def test_login_credenciales_incorrectas(client, usuario_admin):
    response = client.post(
        "/api/auth/login/",
        {"email": "admin@test.com", "password": "WrongPass!"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_email_inexistente(client):
    response = client.post(
        "/api/auth/login/",
        {"email": "noexiste@test.com", "password": "Pass123!"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ── Register ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_registro_crea_usuario_externo(client, grupos):
    response = client.post(
        "/api/auth/register/",
        {
            "email": "nuevo@test.com",
            "password": "Nuevo123!",
            "password_confirmar": "Nuevo123!",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access" in data
    assert data["user"]["grupos"] == ["Externo"]


@pytest.mark.django_db
def test_registro_nunca_asigna_administrador(client, grupos):
    """El endpoint de registro siempre crea usuarios Externos, nunca Admins."""
    client.post(
        "/api/auth/register/",
        {
            "email": "intento@test.com",
            "password": "Intento123!",
            "password_confirmar": "Intento123!",
        },
        format="json",
    )
    from django.contrib.auth import get_user_model
    user = get_user_model().objects.get(email="intento@test.com")
    assert not user.groups.filter(name="Administrador").exists()
    assert user.groups.filter(name="Externo").exists()


@pytest.mark.django_db
def test_registro_email_duplicado(client, usuario_externo):
    response = client.post(
        "/api/auth/register/",
        {
            "email": "externo@test.com",  # ya existe
            "password": "Externo123!",
            "password_confirmar": "Externo123!",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_registro_contrasenas_no_coinciden(client):
    response = client.post(
        "/api/auth/register/",
        {
            "email": "nuevo@test.com",
            "password": "Nuevo123!",
            "password_confirmar": "Diferente123!",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ── Validador de contraseña ───────────────────────────────────────────────────

@pytest.mark.django_db
@pytest.mark.parametrize("password,descripcion", [
    ("password1!",  "sin mayúscula"),
    ("Password!",   "sin dígito"),
    ("Password1",   "sin carácter especial"),
    ("Pw1!",        "demasiado corta (<8)"),
])
def test_contrasena_debil_rechazada(client, password, descripcion):
    response = client.post(
        "/api/auth/register/",
        {
            "email": "test@test.com",
            "password": password,
            "password_confirmar": password,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        f"Contraseña '{password}' ({descripcion}) debería ser rechazada"
    )


@pytest.mark.django_db
def test_contrasena_fuerte_aceptada(client, grupos):
    response = client.post(
        "/api/auth/register/",
        {
            "email": "fuerte@test.com",
            "password": "MiFuerte1!",
            "password_confirmar": "MiFuerte1!",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED


# ── Permisos sobre Empresa ────────────────────────────────────────────────────

@pytest.mark.django_db
def test_externo_no_puede_crear_empresa(client, usuario_externo):
    client.force_authenticate(user=usuario_externo)
    response = client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_puede_crear_empresa(client, usuario_admin):
    client.force_authenticate(user=usuario_admin)
    response = client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_anonimo_no_puede_crear_empresa(client):
    response = client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    # 401 = sin credenciales (JWT activo), 403 = credenciales insuficientes
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_externo_puede_listar_empresas(client, usuario_externo):
    client.force_authenticate(user=usuario_externo)
    response = client.get("/api/empresas/")
    assert response.status_code == status.HTTP_200_OK


# ── JWT token funciona en requests posteriores ────────────────────────────────

@pytest.mark.django_db
def test_jwt_token_permite_crear_empresa(client, usuario_admin):
    # Login y obtener token real
    response = client.post(
        "/api/auth/login/",
        {"email": "admin@test.com", "password": "Admin123!"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    access = response.json()["access"]

    # Usar el token en la cabecera Authorization
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    response = client.post("/api/empresas/", EMPRESA_PAYLOAD, format="json")
    assert response.status_code == status.HTTP_201_CREATED
