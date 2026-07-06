"""
Crea o promueve un usuario al grupo Administrador.

Uso:
    python manage.py crear_admin --email admin@empresa.com --password "MiPass1!"

El registro público (/api/auth/register/) solo permite crear usuarios Externos.
Este comando es la única vía para crear el primer Administrador.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Crea o promueve un usuario al grupo Administrador"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--email", required=True, help="Email del administrador")
        parser.add_argument("--password", required=True, help="Contraseña (mín. 8 chars, mayúscula, dígito, especial)")

    def handle(self, *args, **options) -> None:
        email: str = options["email"]
        password: str = options["password"]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email},
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f"Usuario {email} creado.")
        else:
            self.stdout.write(f"Usuario {email} ya existía — se actualiza solo el rol.")

        grupo_admin, _ = Group.objects.get_or_create(name="Administrador")
        user.groups.add(grupo_admin)

        self.stdout.write(
            self.style.SUCCESS(f"✓  {email} pertenece ahora al grupo Administrador.")
        )
