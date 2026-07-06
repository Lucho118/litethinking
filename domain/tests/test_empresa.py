import pytest
from domain.entities.empresa import Empresa


def test_empresa_valida():
    empresa = Empresa(
        nit="830514226-6",
        nombre="Acme S.A.S.",
        direccion="Calle 1 # 2-3, Bogotá",
        telefono="3001234567",
    )
    assert empresa.nit == "830514226-6"
    assert empresa.nombre == "Acme S.A.S."
    assert empresa.direccion == "Calle 1 # 2-3, Bogotá"
    assert empresa.telefono == "3001234567"


@pytest.mark.parametrize("nit_invalido", [
    "abc-1",          # letras
    "123",            # sin dígito verificador
    "12345678901-1",  # demasiados dígitos
    "123456-",        # verificador vacío
    "123456--1",      # doble guión
    "",               # vacío
])
def test_nit_invalido_lanza_error(nit_invalido):
    with pytest.raises(ValueError, match="NIT"):
        Empresa(nit=nit_invalido, nombre="X", direccion="Y", telefono="Z")


def test_nombre_vacio_lanza_error():
    with pytest.raises(ValueError, match="nombre"):
        Empresa(nit="830514226-6", nombre="   ", direccion="Y", telefono="Z")


def test_nombre_cadena_vacia_lanza_error():
    with pytest.raises(ValueError, match="nombre"):
        Empresa(nit="830514226-6", nombre="", direccion="Y", telefono="Z")


def test_empresa_es_dataclass_mutable():
    empresa = Empresa(nit="830514226-6", nombre="Original", direccion="D", telefono="T")
    empresa.nombre = "Actualizado"
    assert empresa.nombre == "Actualizado"
