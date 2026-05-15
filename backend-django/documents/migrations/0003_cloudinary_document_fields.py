from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0002_pgvector_embedding"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="cloudinary_public_id",
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AddField(
            model_name="document",
            name="cloudinary_resource_type",
            field=models.CharField(blank=True, max_length=24),
        ),
        migrations.AddField(
            model_name="document",
            name="cloudinary_secure_url",
            field=models.URLField(blank=True, max_length=2048),
        ),
        migrations.AddField(
            model_name="document",
            name="original_filename",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
