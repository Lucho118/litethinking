from datetime import datetime, timezone

import pytest

from domain.entities.bloque_auditoria import HASH_GENESIS, BloqueAuditoria


# ── Helpers ───────────────────────────────────────────────────────────────────

_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _bloque(
    indice: int = 0,
    entidad: str = "Empresa",
    accion: str = "CREAR",
    datos: dict | None = None,
    hash_anterior: str = HASH_GENESIS,
) -> BloqueAuditoria:
    return BloqueAuditoria(
        indice=indice,
        timestamp=_TS,
        entidad=entidad,
        entidad_id="830514226-6",
        accion=accion,
        datos=datos or {"nombre": "Acme"},
        hash_anterior=hash_anterior,
    )


# ── Hash determinism ──────────────────────────────────────────────────────────

def test_mismo_input_produce_mismo_hash():
    assert _bloque().hash_actual == _bloque().hash_actual


def test_cambiar_indice_cambia_hash():
    assert _bloque(indice=0).hash_actual != _bloque(indice=1).hash_actual


def test_cambiar_entidad_cambia_hash():
    assert _bloque(entidad="Empresa").hash_actual != _bloque(entidad="Producto").hash_actual


def test_cambiar_accion_cambia_hash():
    assert _bloque(accion="CREAR").hash_actual != _bloque(accion="EDITAR").hash_actual


def test_cambiar_datos_cambia_hash():
    b1 = _bloque(datos={"nombre": "Original"})
    b2 = _bloque(datos={"nombre": "Modificado"})
    assert b1.hash_actual != b2.hash_actual


def test_cambiar_hash_anterior_cambia_hash():
    b1 = _bloque(hash_anterior=HASH_GENESIS)
    b2 = _bloque(hash_anterior="a" * 64)
    assert b1.hash_actual != b2.hash_actual


# ── es_integro ────────────────────────────────────────────────────────────────

def test_bloque_recien_creado_es_integro():
    assert _bloque().es_integro() is True


def test_bloque_con_datos_alterados_no_es_integro():
    b = _bloque()
    b.datos = {"nombre": "Alterado por ataque"}  # modificar post-creación
    assert b.es_integro() is False


# ── es_valido ─────────────────────────────────────────────────────────────────

def test_bloque_genesis_es_valido_sin_anterior():
    assert _bloque(indice=0).es_valido(bloque_anterior=None) is True


def test_bloque_genesis_con_hash_anterior_incorrecto_no_es_valido():
    b = BloqueAuditoria(
        indice=0, timestamp=_TS, entidad="Empresa", entidad_id="X",
        accion="CREAR", datos={}, hash_anterior="hash_incorrecto",
    )
    assert b.es_valido(bloque_anterior=None) is False


def test_cadena_de_dos_bloques_valida():
    b0 = _bloque(indice=0)
    b1 = _bloque(indice=1, accion="EDITAR", hash_anterior=b0.hash_actual)
    assert b1.es_valido(bloque_anterior=b0) is True


def test_bloque_con_hash_anterior_incorrecto_no_es_valido():
    b0 = _bloque(indice=0)
    b1 = _bloque(indice=1, accion="EDITAR", hash_anterior="hash_falso_" + "x" * 53)
    assert b1.es_valido(bloque_anterior=b0) is False


def test_bloque_alterado_detectado_al_verificar_ese_bloque():
    """
    Alterar los datos de b0 hace que b0.es_integro() → False.
    La ruptura se detecta al validar b0 (no b1): b0.es_valido(None) devuelve False.
    Así funciona la verificación de cadena del repositorio:
    procesa cada bloque en orden y llama es_valido() sobre él.
    """
    b0 = _bloque(indice=0)
    _b1 = _bloque(indice=1, accion="EDITAR", hash_anterior=b0.hash_actual)
    b0.datos = {"nombre": "Manipulado"}   # alterar b0 después de crear b1
    # La ruptura se detecta en b0, no en b1
    assert b0.es_integro() is False
    assert b0.es_valido(bloque_anterior=None) is False


# ── Carga desde BD (hash ya calculado) ───────────────────────────────────────

def test_bloque_cargado_desde_db_no_recalcula_hash():
    original = _bloque()
    hash_guardado = original.hash_actual

    cargado = BloqueAuditoria(
        indice=original.indice,
        timestamp=original.timestamp,
        entidad=original.entidad,
        entidad_id=original.entidad_id,
        accion=original.accion,
        datos=original.datos,
        hash_anterior=original.hash_anterior,
        hash_actual=hash_guardado,      # se pasa el hash ya existente
    )
    assert cargado.hash_actual == hash_guardado
    assert cargado.es_integro() is True
