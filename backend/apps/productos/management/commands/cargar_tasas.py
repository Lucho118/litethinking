"""
Management command para cargar tasas de cambio iniciales.

Uso:
    python manage.py cargar_tasas

En producción, este comando sería ejecutado por un job periódico (Celery beat,
cron, etc.) que obtendría las tasas actualizadas de una API como:
https://exchangerate-api.com o https://openexchangerates.org
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.productos.models import TasaCambioModel


class Command(BaseCommand):
    help = "Carga tasas de cambio iniciales (COP ↔ USD ↔ EUR)"

    # Tasas aproximadas — actualizar manualmente o automatizar con API externa
    TASAS: list[tuple[str, str, Decimal]] = [
        ("COP", "USD", Decimal("0.00024000")),  # 1 COP ≈ 0.00024 USD
        ("COP", "EUR", Decimal("0.00022000")),  # 1 COP ≈ 0.00022 EUR
        ("USD", "COP", Decimal("4166.67000000")),
        ("USD", "EUR", Decimal("0.91670000")),
        ("EUR", "COP", Decimal("4545.45000000")),
        ("EUR", "USD", Decimal("1.09000000")),
    ]

    def handle(self, *args, **options) -> None:
        for origen, destino, tasa in self.TASAS:
            obj, created = TasaCambioModel.objects.update_or_create(
                moneda_origen=origen,
                moneda_destino=destino,
                defaults={"tasa": tasa},
            )
            accion = "creada" if created else "actualizada"
            self.stdout.write(f"  1 {origen} = {tasa} {destino} — {accion}")

        self.stdout.write(self.style.SUCCESS("\nTasas de cambio cargadas exitosamente."))
