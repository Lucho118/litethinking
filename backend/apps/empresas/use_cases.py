from __future__ import annotations

from domain.entities.empresa import Empresa
from .repositories import EmpresaRepository


class CrearEmpresaUseCase:
    def __init__(self, repository: EmpresaRepository) -> None:
        self.repository = repository

    def ejecutar(self, nit: str, nombre: str, direccion: str, telefono: str) -> Empresa:
        if self.repository.obtener(nit) is not None:
            raise ValueError(f"Ya existe una empresa con NIT '{nit}'.")
        # Domain entity validates business rules (NIT format, nombre not empty)
        empresa = Empresa(nit=nit, nombre=nombre, direccion=direccion, telefono=telefono)
        return self.repository.guardar(empresa)


class ObtenerEmpresaUseCase:
    def __init__(self, repository: EmpresaRepository) -> None:
        self.repository = repository

    def ejecutar(self, nit: str) -> Empresa | None:
        return self.repository.obtener(nit)


class ListarEmpresasUseCase:
    def __init__(self, repository: EmpresaRepository) -> None:
        self.repository = repository

    def ejecutar(self) -> list[Empresa]:
        return self.repository.listar()


class ActualizarEmpresaUseCase:
    def __init__(self, repository: EmpresaRepository) -> None:
        self.repository = repository

    def ejecutar(self, nit: str, nombre: str, direccion: str, telefono: str) -> Empresa:
        if self.repository.obtener(nit) is None:
            raise ValueError(f"No existe ninguna empresa con NIT '{nit}'.")
        empresa = Empresa(nit=nit, nombre=nombre, direccion=direccion, telefono=telefono)
        return self.repository.guardar(empresa)


class EliminarEmpresaUseCase:
    def __init__(self, repository: EmpresaRepository) -> None:
        self.repository = repository

    def ejecutar(self, nit: str) -> None:
        if self.repository.obtener(nit) is None:
            raise ValueError(f"No existe ninguna empresa con NIT '{nit}'.")
        self.repository.eliminar(nit)
