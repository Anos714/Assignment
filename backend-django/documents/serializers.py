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
            "original_filename",
            "file_type",
            "mime_type",
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
        original_filename = Path(uploaded_file.name).name
        cloudinary_upload = upload_to_cloudinary_if_configured(
            uploaded_file,
            user_id=self.context["request"].user.id,
        )
        uploaded_file.seek(0)
        document = Document.objects.create(
            user=self.context["request"].user,
            filename=original_filename,
            original_filename=original_filename,
            file_type=extension,
            mime_type=getattr(uploaded_file, "content_type", "") or cloudinary_upload.get("format", ""),
            file=uploaded_file,
            storage_key="",
            file_size=uploaded_file.size,
            cloudinary_public_id=cloudinary_upload.get("public_id", ""),
            cloudinary_secure_url=cloudinary_upload.get("secure_url", ""),
            cloudinary_resource_type=cloudinary_upload.get("resource_type", ""),
        )
        document.storage_key = document.cloudinary_secure_url or document.file.name
        document.save(update_fields=("storage_key", "updated_at"))
        return document


def upload_to_cloudinary_if_configured(uploaded_file, *, user_id) -> dict:
    if not all(
        (
            settings.CLOUDINARY_CLOUD_NAME,
            settings.CLOUDINARY_API_KEY,
            settings.CLOUDINARY_API_SECRET,
        )
    ):
        return {}

    try:
        import cloudinary
        import cloudinary.uploader

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        return cloudinary.uploader.upload(
            uploaded_file,
            resource_type="raw",
            folder=f"documindai/users/{user_id}/documents",
        )
    except Exception as exc:
        raise serializers.ValidationError({"file": f"Could not upload file to Cloudinary: {exc}"}) from exc
