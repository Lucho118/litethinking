from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("productos", "0002_add_embedding"),
    ]

    operations = [
        migrations.AddField(
            model_name="productomodel",
            name="cantidad",
            field=models.PositiveIntegerField(default=0, verbose_name="Cantidad en inventario"),
        ),
    ]
