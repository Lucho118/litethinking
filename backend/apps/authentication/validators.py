import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class FuertePasswordValidator:
    """
    Complementa los validadores built-in de Django exigiendo complejidad:
      - Mínimo 8 caracteres (también lo verifica MinimumLengthValidator)
      - Al menos una letra mayúscula
      - Al menos un dígito
      - Al menos un carácter especial  (!@#$%^&*…)

    Registrar en AUTH_PASSWORD_VALIDATORS en config/settings/base.py.
    """

    ESPECIALES = r"""[!@#$%^&*()\-_=+\[\]{};:'",.<>/?\\|`~]"""

    def validate(self, password: str, user=None) -> None:
        errores: list[str] = []

        if len(password) < 8:
            errores.append("al menos 8 caracteres")
        if not re.search(r"[A-Z]", password):
            errores.append("al menos una letra mayúscula")
        if not re.search(r"\d", password):
            errores.append("al menos un dígito")
        if not re.search(self.ESPECIALES, password):
            errores.append("al menos un carácter especial (!@#$%…)")

        if errores:
            raise ValidationError(
                _("La contraseña debe contener: %(requisitos)s."),
                code="password_demasiado_simple",
                params={"requisitos": ", ".join(errores)},
            )

    def get_help_text(self) -> str:
        return _(
            "Tu contraseña debe tener mínimo 8 caracteres e incluir "
            "una mayúscula, un dígito y un carácter especial."
        )
