from django.db import migrations


def crear_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="Administrador")
    Group.objects.get_or_create(name="Externo")


def eliminar_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Administrador", "Externo"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        # Garantiza que el modelo Group de Django ya existe
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(crear_grupos, reverse_code=eliminar_grupos),
    ]
