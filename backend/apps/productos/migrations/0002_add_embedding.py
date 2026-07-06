from django.db import migrations


def habilitar_pgvector(apps, schema_editor):
    """
    Habilita la extensión pgvector y agrega la columna embedding.
    Solo se ejecuta en PostgreSQL — en SQLite (tests) se omite silenciosamente.

    Decisión: esta migración vive en backend/apps/productos/ porque ProductoModel
    es dueño de la tabla 'productos'. El microservicio FastAPI (ai-agent) accede
    a la columna via SQL raw/SQLAlchemy, sin tocar el ORM de Django.
    """
    if schema_editor.connection.vendor != "postgresql":
        return  # SQLite en tests: skip

    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    schema_editor.execute(
        "ALTER TABLE productos ADD COLUMN IF NOT EXISTS embedding vector(1536);"
    )
    # Índice HNSW para búsqueda aproximada eficiente (cosine distance)
    schema_editor.execute(
        """
        CREATE INDEX IF NOT EXISTS productos_embedding_hnsw
        ON productos
        USING hnsw (embedding vector_cosine_ops);
        """
    )


def eliminar_embedding(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("DROP INDEX IF EXISTS productos_embedding_hnsw;")
    schema_editor.execute("ALTER TABLE productos DROP COLUMN IF EXISTS embedding;")


class Migration(migrations.Migration):
    dependencies = [
        ("productos", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(habilitar_pgvector, reverse_code=eliminar_embedding),
    ]
