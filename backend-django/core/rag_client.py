import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


@dataclass(frozen=True)
class RagClient:
    base_url: str | None = None
    timeout: float | None = None

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        base_url = self.base_url or settings.RAG_SERVICE_URL
        timeout = self.timeout or settings.RAG_TIMEOUT_SECONDS
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RagServiceError(str(exc)) from exc

    def ingest_document(self, *, document_id: str, user_id: str, storage_key: str, file_type: str):
        return self.post(
            "/internal/ingest",
            {
                "document_id": document_id,
                "user_id": user_id,
                "storage_key": storage_key,
                "file_type": file_type,
            },
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
