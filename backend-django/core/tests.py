from urllib.error import HTTPError, URLError
from unittest.mock import patch

from django.test import Client, SimpleTestCase

from core.rag_client import RagClient, RagServiceError


class HealthCheckTests(SimpleTestCase):
    def test_health_endpoint_returns_ok_without_authentication(self):
        for path in ("/health", "/health/"):
            with self.subTest(path=path):
                response = Client().get(path)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"status": "ok"})


class RagClientRetryTests(SimpleTestCase):
    def test_ingest_retries_temporary_http_errors(self):
        response = _JsonResponse(b'{"status": "ready", "chunk_count": 3}')
        temporary_error = HTTPError(
            url="http://rag/internal/ingest",
            code=502,
            msg="Bad Gateway",
            hdrs=None,
            fp=None,
        )

        with (
            patch("core.rag_client.urlopen", side_effect=[temporary_error, temporary_error, response]) as urlopen,
            patch("core.rag_client.time.sleep") as sleep,
            self.assertLogs("core.rag_client", level="WARNING") as logs,
        ):
            result = RagClient(base_url="http://rag", timeout=1).ingest_document(
                document_id="doc-1",
                user_id="user-1",
                storage_key="documents/doc.txt",
                file_type="txt",
                filename="doc.txt",
                file_url="https://res.cloudinary.com/demo/raw/upload/doc.txt",
                mime_type="text/plain",
            )

        self.assertEqual(result, {"status": "ready", "chunk_count": 3})
        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual(sleep.call_count, 2)
        sleep.assert_called_with(3)
        self.assertEqual(len(logs.output), 2)

    def test_ingest_retries_connection_errors(self):
        response = _JsonResponse(b'{"status": "ready"}')

        with (
            patch("core.rag_client.urlopen", side_effect=[URLError("connection refused"), response]) as urlopen,
            patch("core.rag_client.time.sleep") as sleep,
            self.assertLogs("core.rag_client", level="WARNING") as logs,
        ):
            result = RagClient(base_url="http://rag", timeout=1).ingest_document(
                document_id="doc-1",
                user_id="user-1",
                storage_key="documents/doc.txt",
                file_type="txt",
            )

        self.assertEqual(result, {"status": "ready"})
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(3)
        self.assertEqual(len(logs.output), 1)

    def test_ingest_does_not_retry_client_http_errors(self):
        not_found = HTTPError(
            url="http://rag/internal/ingest",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None,
        )

        with (
            patch("core.rag_client.urlopen", side_effect=not_found) as urlopen,
            patch("core.rag_client.time.sleep") as sleep,
        ):
            with self.assertRaisesMessage(RagServiceError, "HTTP Error 404: Not Found"):
                RagClient(base_url="http://rag", timeout=1).ingest_document(
                    document_id="doc-1",
                    user_id="user-1",
                    storage_key="documents/doc.txt",
                    file_type="txt",
                )

        urlopen.assert_called_once()
        sleep.assert_not_called()


class _JsonResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body
