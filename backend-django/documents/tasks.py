import logging
import mimetypes

from celery import shared_task

from core.rag_client import RagClient, RagServiceError
from documents.models import Document, DocumentStatus


logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(RagServiceError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def ingest_document_task(self, document_id: str) -> dict:
    document = Document.objects.get(id=document_id)
    document.status = DocumentStatus.PROCESSING
    document.error_message = ""
    document.save(update_fields=("status", "error_message", "updated_at"))

    filename = document.original_filename or document.filename
    file_url = document.cloudinary_secure_url or None
    storage_key = document.cloudinary_secure_url or document.storage_key
    mime_type = _document_mime_type(document, filename)
    payload = {
        "document_id": str(document.id),
        "user_id": str(document.user_id),
        "filename": filename,
        "file_url": file_url,
        "storage_key": storage_key,
        "file_type": document.file_type,
        "mime_type": mime_type,
    }
    logger.info(
        "Sending document ingestion payload to RAG service",
        extra={
            "document_id": payload["document_id"],
            "user_id": payload["user_id"],
            "document_filename": filename,
            "file_url": file_url,
            "storage_key": storage_key,
            "file_type": document.file_type,
            "mime_type": mime_type,
            "has_file_url": bool(file_url),
        },
    )

    try:
        response = RagClient().ingest_document(
            **payload,
        )
    except RagServiceError as exc:
        logger.exception(
            "Document ingestion request failed",
            extra={
                "document_id": str(document.id),
                "user_id": str(document.user_id),
                "has_file_url": bool(file_url),
            },
        )
        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)[:2000]
        document.save(update_fields=("status", "error_message", "updated_at"))
        raise

    status = response.get("status")
    document.status = status if status in DocumentStatus.values else DocumentStatus.FAILED
    document.chunk_count = int(response.get("chunk_count") or 0)
    document.error_message = response.get("error_message") or ""
    document.save(update_fields=("status", "chunk_count", "error_message", "updated_at"))
    return response


def _document_mime_type(document: Document, filename: str) -> str | None:
    content_type = getattr(getattr(document, "file", None), "content_type", None)
    if content_type:
        return content_type
    guessed_type = mimetypes.guess_type(filename)[0]
    if guessed_type:
        return guessed_type
    return {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
    }.get(document.file_type)
