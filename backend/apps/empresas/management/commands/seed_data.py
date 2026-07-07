"""
Management command para cargar datos de prueba.

Crea 3 empresas y ~5 productos por empresa para poder probar todos los endpoints
sin necesidad de insertar datos manualmente via API.

Uso:
    python manage.py seed_data            # Crea los datos (idempotente)
    python manage.py seed_data --reset    # Borra todo y recrea desde cero

NOTA: Los embeddings (pgvector) NO se generan aqui.
      Para vectorizar, corre el script del microservicio:
          cd microservices/ai-agent && python scripts/vectorizar_productos.py
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.empresas.models import EmpresaModel
from apps.productos.models import ProductoModel


# ---------------------------------------------------------------------------
# Datos de prueba
# ---------------------------------------------------------------------------

EMPRESAS = [
    {
        "nit": "900123456-1",
        "nombre": "TechCo Colombia S.A.S",
        "direccion": "Cra 7 # 32-16, Bogota D.C.",
        "telefono": "+573001234567",
    },
    {
        "nit": "800987654-2",
        "nombre": "Distribuidora Nacional Ltda",
        "direccion": "Av 6 de Diciembre y Naciones Unidas, Quito",
        "telefono": "+571987654321",
    },
    {
        "nit": "700456789-3",
        "nombre": "Agro Sur E.U.",
        "direccion": "Carrera 15 # 100-05, Medellin",
        "telefono": "+576004567890",
    },
]

PRODUCTOS = [
    # TechCo Colombia
    {"codigo": "TCO-001", "nombre": "Laptop Ultrabook Pro 14", "caracteristicas": "Procesador Intel Core i7, 16GB RAM, 512GB SSD NVMe, pantalla IPS 14 pulgadas Full HD, bateria 12 horas, peso 1.2 kg, Windows 11 Pro", "precio_base": Decimal("4500000"), "moneda_base": "COP", "empresa_nit": "900123456-1", "cantidad": 12},
    {"codigo": "TCO-002", "nombre": "Monitor Curvo 27 144Hz", "caracteristicas": "Panel VA curvo 1500R, resolucion 2560x1440 QHD, tasa de refresco 144Hz, tiempo de respuesta 1ms, compatible FreeSync y G-Sync, HDMI x2, DisplayPort x1", "precio_base": Decimal("1200000"), "moneda_base": "COP", "empresa_nit": "900123456-1", "cantidad": 8},
    {"codigo": "TCO-003", "nombre": "Teclado Mecanico RGB TKL", "caracteristicas": "Switches Cherry MX Red, layout TKL sin numpad, iluminacion RGB por tecla, marco aluminio, cable USB-C desmontable, anti-ghosting completo", "precio_base": Decimal("280000"), "moneda_base": "COP", "empresa_nit": "900123456-1", "cantidad": 25},
    {"codigo": "TCO-004", "nombre": "Mouse Inalambrico Ergonomico", "caracteristicas": "Sensor optico 4000 DPI ajustable, conexion Bluetooth y USB dongle, bateria recargable USB-C, 6 botones programables, diseno ergonomico para mano derecha, alcance 10m", "precio_base": Decimal("150000"), "moneda_base": "COP", "empresa_nit": "900123456-1", "cantidad": 40},
    {"codigo": "TCO-005", "nombre": "Hub USB-C 7 en 1", "caracteristicas": "USB-C Power Delivery 100W, HDMI 4K@60Hz, 3x USB-A 3.0, lector SD/MicroSD, compatible macOS y Windows, carcasa aluminio, cable integrado 20cm", "precio_base": Decimal("95000"), "moneda_base": "COP", "empresa_nit": "900123456-1", "cantidad": 15},
    # Distribuidora Nacional
    {"codigo": "DNL-001", "nombre": "Aceite de Cocina Girasol 3L", "caracteristicas": "Aceite vegetal 100% girasol, alto en vitamina E, sin colesterol, prensado en frio, botella PET reciclable 3 litros, apto para freir a alta temperatura", "precio_base": Decimal("18500"), "moneda_base": "COP", "empresa_nit": "800987654-2", "cantidad": 200},
    {"codigo": "DNL-002", "nombre": "Arroz Premium Extra Largo x5kg", "caracteristicas": "Variedad indica grano largo, sin gluten, tiempo de coccion 18 min, rendimiento 1:3, empaque hermetico resellable 5kg, cultivo colombiano", "precio_base": Decimal("22000"), "moneda_base": "COP", "empresa_nit": "800987654-2", "cantidad": 150},
    {"codigo": "DNL-003", "nombre": "Detergente Liquido Concentrado 2L", "caracteristicas": "Formula ultra concentrada 1 tapa 20 cargas, aroma lavanda y vainilla, para ropa de color y blanca, biodegradable, envase con tapon dosificador", "precio_base": Decimal("32000"), "moneda_base": "COP", "empresa_nit": "800987654-2", "cantidad": 80},
    {"codigo": "DNL-004", "nombre": "Papel Higienico x24 rollos", "caracteristicas": "Triple hoja suave, 200 hojas por rollo, papel 100% puro celulosa, sin perfumes ni colorantes, empaque individual biodegradable", "precio_base": Decimal("28000"), "moneda_base": "COP", "empresa_nit": "800987654-2", "cantidad": 300},
    # Agro Sur
    {"codigo": "AGR-001", "nombre": "Fertilizante NPK 15-15-15 x50kg", "caracteristicas": "Formula balanceada nitrogeno-fosforo-potasio 15-15-15, grano uniforme soluble en agua, apto para cultivos de maiz, papa, cafe y hortalizas, certificado ICA", "precio_base": Decimal("85000"), "moneda_base": "COP", "empresa_nit": "700456789-3", "cantidad": 50},
    {"codigo": "AGR-002", "nombre": "Herbicida Selectivo 1L", "caracteristicas": "Control de malezas de hoja ancha en gramineas, concentrado emulsionable, aplicar 1L por ha, periodo de carencia 15 dias, registro ICA vigente, no afecta cultivos de maiz ni sorgo", "precio_base": Decimal("45000"), "moneda_base": "COP", "empresa_nit": "700456789-3", "cantidad": 30},
    {"codigo": "AGR-003", "nombre": "Manguera de Goteo 100m", "caracteristicas": "Diametro interno 16mm, goteros integrados cada 30cm, caudal 2 L/h por gotero, presion operacion 1-3 bar, material LLDPE UV resistente, vida util 5 temporadas", "precio_base": Decimal("120000"), "moneda_base": "COP", "empresa_nit": "700456789-3", "cantidad": 20},
    {"codigo": "AGR-004", "nombre": "Semillas de Tomate Chonto x500g", "caracteristicas": "Variedad Chonto mejorada, germinacion mayor 95%, ciclo 90 dias desde trasplante, resistente a fusarium, rendimiento estimado 40 ton por ha, temperatura optima 18-28C", "precio_base": Decimal("38000"), "moneda_base": "COP", "empresa_nit": "700456789-3", "cantidad": 100},
]


class Command(BaseCommand):
    help = "Carga datos de prueba: 3 empresas y 13 productos"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina todos los datos existentes antes de insertar",
        )

    def handle(self, *args, **options) -> None:
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Eliminando datos existentes..."))
            ProductoModel.objects.filter(codigo__in=[p["codigo"] for p in PRODUCTOS]).delete()
            EmpresaModel.objects.filter(nit__in=[e["nit"] for e in EMPRESAS]).delete()
            self.stdout.write("  Datos eliminados.")

        # --- Empresas ---
        self.stdout.write("\nCreando empresas...")
        empresas_creadas = 0
        for datos in EMPRESAS:
            _, created = EmpresaModel.objects.get_or_create(
                nit=datos["nit"],
                defaults={
                    "nombre": datos["nombre"],
                    "direccion": datos["direccion"],
                    "telefono": datos["telefono"],
                },
            )
            estado = self.style.SUCCESS("creada") if created else "ya existia"
            self.stdout.write(f"  [{datos['nit']}] {datos['nombre']} -- {estado}")
            if created:
                empresas_creadas += 1

        # --- Productos ---
        self.stdout.write("\nCreando productos...")
        productos_creados = 0
        for datos in PRODUCTOS:
            empresa = EmpresaModel.objects.get(nit=datos["empresa_nit"])
            _, created = ProductoModel.objects.get_or_create(
                codigo=datos["codigo"],
                defaults={
                    "nombre": datos["nombre"],
                    "caracteristicas": datos["caracteristicas"],
                    "precio_base": datos["precio_base"],
                    "moneda_base": datos["moneda_base"],
                    "empresa": empresa,
                    "cantidad": datos["cantidad"],
                },
            )
            estado = self.style.SUCCESS("creado") if created else "ya existia"
            self.stdout.write(f"  [{datos['codigo']}] {datos['nombre']} -- {estado}")
            if created:
                productos_creados += 1

        # --- Resumen ---
        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeed completado: {empresas_creadas} empresa(s) y "
                f"{productos_creados} producto(s) creados."
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "\nRECUERDA: los embeddings NO se generan automaticamente.\n"
                "Para vectorizar los productos (necesario para el agente IA), corre:\n"
                "  cd microservices/ai-agent && python scripts/vectorizar_productos.py"
            )
        )
