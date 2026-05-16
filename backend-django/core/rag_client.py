import json
import logging
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


logger = logging.getLogger(__name__)
RETRYABLE_INGEST_STATUS_CODES = {502, 503, 504}
INGEST_RETRY_ATTEMPTS = 3
INGEST_RETRY_DELAY_SECONDS = 3


@dataclass(frozen=True)
class RagClient:
    base_url: str | None = None
    timeout: float | None = None

    def post(
        self,
        path: str,
        payload: dict[str, Any],
        *,
        retry_status_codes: set[int] | None = None,
        attempts: int = 1,
        retry_delay_seconds: float = 0,
    ) -> dict[str, Any]:
        base_url = self.base_url or settings.RAG_SERVICE_URL
        timeout = self.timeout or settings.RAG_TIMEOUT_SECONDS
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        retry_status_codes = retry_status_codes or set()

        for attempt in range(1, attempts + 1):
            try:
                with urlopen(request, timeout=timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                if exc.code in retry_status_codes and attempt < attempts:
                    self._log_retry(path, attempt, attempts, retry_delay_seconds, exc)
                    time.sleep(retry_delay_seconds)
                    continue
                raise RagServiceError(str(exc)) from exc
            except (URLError, TimeoutError) as exc:
                if attempt < attempts:
                    self._log_retry(path, attempt, attempts, retry_delay_seconds, exc)
                    time.sleep(retry_delay_seconds)
                    continue
                raise RagServiceError(str(exc)) from exc
            except json.JSONDecodeError as exc:
                raise RagServiceError(str(exc)) from exc

        raise RagServiceError("RAG service request failed.")

    def _log_retry(
        self,
        path: str,
        attempt: int,
        attempts: int,
        retry_delay_seconds: float,
        exc: Exception,
    ) -> None:
        logger.warning(
            "RAG service request failed; retrying",
            extra={
                "path": path,
                "attempt": attempt,
                "next_attempt": attempt + 1,
                "max_attempts": attempts,
                "retry_delay_seconds": retry_delay_seconds,
                "error": str(exc),
            },
        )

    def ingest_document(
        self,
        *,
        document_id: str,
        user_id: str,
        storage_key: str,
        file_type: str,
        filename: str | None = None,
        file_url: str | None = None,
        mime_type: str | None = None,
    ):
        return self.post(
            "/internal/ingest",
            {
                "document_id": document_id,
                "user_id": user_id,
                "filename": filename,
                "file_url": file_url,
                "storage_key": storage_key,
                "file_type": file_type,
                "mime_type": mime_type,
            },
            retry_status_codes=RETRYABLE_INGEST_STATUS_CODES,
            attempts=INGEST_RETRY_ATTEMPTS,
            retry_delay_seconds=INGEST_RETRY_DELAY_SECONDS,
        )

    def ask(
        self,
        *,
        user_id: str,
        chat_id: str,
        question: str,
        document_ids: list[str],
        top_k: int = 5,
    ) -> dict[str, Any]:
        return self.post(
            "/internal/ask",
            {
                "user_id": user_id,
                "chat_id": chat_id,
                "question": question,
                "document_ids": document_ids,
                "top_k": top_k,
            },
        )


class RagServiceError(RuntimeError):
    pass
