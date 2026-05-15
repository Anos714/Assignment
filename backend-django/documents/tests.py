from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from unittest.mock import patch

from accounts.models import User
from documents.models import Document
from documents.tasks import ingest_document_task


@override_settings(CLOUDINARY_CLOUD_NAME="", CLOUDINARY_API_KEY="", CLOUDINARY_API_SECRET="")
class DocumentApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="docs@example.com",
            password="StrongPass123!",
            full_name="Docs User",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_upload_rejects_unsupported_file_type(self):
        response = self.client.post(
            "/api/documents/",
            {"file": SimpleUploadedFile("notes.exe", b"bad")},
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("file", response.data)

    def test_upload_creates_queued_document(self):
        response = self.client.post(
            "/api/documents/",
            {"file": SimpleUploadedFile("notes.txt", b"hello")},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["filename"], "notes.txt")
        self.assertEqual(response.data["file_type"], "txt")
        self.assertEqual(response.data["status"], "queued")

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @patch("documents.tasks.RagClient.ingest_document")
    def test_ingestion_task_marks_document_ready(self, ingest_document):
        document = Document.objects.create(
            user=self.user,
            filename="source.txt",
            original_filename="source.txt",
            file_type="txt",
            file=SimpleUploadedFile("source.txt", b"hello"),
            storage_key="documents/source.txt",
            file_size=5,
        )
        ingest_document.return_value = {
            "document_id": str(document.id),
            "status": "ready",
            "chunk_count": 2,
        }

        result = ingest_document_task(str(document.id))

        document.refresh_from_db()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(document.status, "ready")
        self.assertEqual(document.chunk_count, 2)
        ingest_document.assert_called_once()
        payload = ingest_document.call_args.kwargs
        self.assertEqual(payload["filename"], "source.txt")
        self.assertEqual(payload["storage_key"], "documents/source.txt")
        self.assertEqual(payload["file_url"], "")
        self.assertEqual(payload["mime_type"], "")
