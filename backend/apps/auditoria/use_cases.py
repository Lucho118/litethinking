from domain.entities.bloque_auditoria import BloqueAuditoria

from .repositories import AuditoriaRepository


class RegistrarAuditoriaUseCase:
    """
    Punto de entrada único para registrar cualquier operación auditable.
    Los signals de EmpresaModel y ProductoModel lo llaman automáticamente.
    """

    def __init__(self, repository: AuditoriaRepository) -> None:
        self.repository = repository

    def ejecutar(
        self,
        entidad: str,
        entidad_id: str,
        accion: str,
        datos: dict,
    ) -> BloqueAuditoria:
        return self.repository.guardar_bloque(
            entidad=entidad,
            entidad_id=entidad_id,
            accion=accion,
            datos=datos,
        )
