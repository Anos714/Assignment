from pathlib import Path

from django.conf import settings
from rest_framework import serializers

from documents.models import Document


ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "id",
            "filename",
            "file_type",
            "status",
            "file_size",
            "chunk_count",
            "error_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class DocumentUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = Document
        fields = ("id", "file", "filename", "file_type", "status", "file_size", "created_at")
        read_only_fields = ("id", "filename", "file_type", "status", "file_size", "created_at")

    def validate_file(self, uploaded_file):
        extension = Path(uploaded_file.name).suffix.lower().removeprefix(".")
        if extension not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError("Only PDF, DOCX, and TXT files are supported.")
        if uploaded_file.size > settings.MAX_DOCUMENT_UPLOAD_BYTES:
            raise serializers.ValidationError("File exceeds the maximum upload size.")
        return uploaded_file

    def create(self, validated_data):
        uploaded_file = validated_data["file"]
        extension = Path(uploaded_file.name).suffix.lower().removeprefix(".")
        document = Document.objects.create(
            user=self.context["request"].user,
            filename=Path(uploaded_file.name).name,
            file_type=extension,
            file=uploaded_file,
            storage_key="",
            file_size=uploaded_file.size,
        )
        document.storage_key = document.file.name
        document.save(update_fields=("storage_key", "updated_at"))
        return document

