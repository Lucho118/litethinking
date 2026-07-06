from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"
    verbose_name = "Autenticación"

    def ready(self):
        _patch_django_context_copy_for_python314()


def _patch_django_context_copy_for_python314():
    """
    Python 3.14 rompe django.template.context.BaseContext.__copy__.

    En Python <= 3.13, copy(super()) dentro de __copy__ funcionaba porque
    copy() seguía el método __copy__ del objeto subyacente.
    En Python 3.14, copy(super()) devuelve el proxy super sin copiar el
    objeto real, por lo que la asignación duplicate.dicts falla con:
        AttributeError: 'super' object has no attribute 'dicts'

    Solución: reemplazar __copy__ para crear la copia directamente.
    """
    from copy import copy
    from django.template.context import BaseContext, Context

    def _base_context_copy(self):
        cls = type(self)
        duplicate = cls.__new__(cls)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    def _context_copy(self):
        duplicate = _base_context_copy(self)
        duplicate.render_context = copy(self.render_context)
        return duplicate

    BaseContext.__copy__ = _base_context_copy
    Context.__copy__ = _context_copy
