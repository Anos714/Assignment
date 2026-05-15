import uuid

from django.conf import settings
from django.db import models


class DocumentStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    PROCESSING = "processing", "Processing"
    READY = "ready", "Ready"
    FAILED = "failed", "Failed"


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents")
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=12)
    file = models.FileField(upload_to="documents/%Y/%m/%d/")
    storage_key = models.CharField(max_length=512)
    cloudinary_public_id = models.CharField(max_length=512, blank=True)
    cloudinary_secure_url = models.URLField(max_length=1000, blank=True)
    cloudinary_resource_type = models.CharField(max_length=50, blank=True)
    mime_type = models.CharField(max_length=120, blank=True)
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.QUEUED,
        db_index=True,
    )
    file_size = models.PositiveBigIntegerField()
    chunk_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("user", "status")),
            models.Index(fields=("created_at",)),
        ]

    def __str__(self) -> str:
        return self.filename


class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="document_chunks")
    chunk_index = models.PositiveIntegerField()
    page_number = models.PositiveIntegerField(null=True, blank=True)
    content = models.TextField()
    embedding = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("chunk_index",)
        constraints = [
            models.UniqueConstraint(
                fields=("document", "chunk_index"),
                name="unique_chunk_index_per_document",
            )
        ]
        indexes = [
            models.Index(fields=("user", "document")),
        ]
