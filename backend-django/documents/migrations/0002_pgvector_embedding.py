from django.db import migrations


def enable_pgvector(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cursor.execute(
            """
            ALTER TABLE documents_documentchunk
            ALTER COLUMN embedding TYPE vector(384)
            USING CASE
                WHEN embedding IS NULL THEN NULL
                ELSE embedding::text::vector(384)
            END
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS document_chunks_embedding_hnsw
            ON documents_documentchunk
            USING hnsw (embedding vector_cosine_ops)
            """
        )


def disable_pgvector(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP INDEX IF EXISTS document_chunks_embedding_hnsw")
        cursor.execute(
            """
            ALTER TABLE documents_documentchunk
            ALTER COLUMN embedding TYPE jsonb
            USING CASE
                WHEN embedding IS NULL THEN NULL
                ELSE to_jsonb(embedding::text)
            END
            """
        )


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(enable_pgvector, disable_pgvector),
    ]
