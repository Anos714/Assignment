from celery import shared_task

from core.rag_client import RagClient, RagServiceError
from documents.models import Document, DocumentStatus


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

    try:
        response = RagClient().ingest_document(
            document_id=str(document.id),
            user_id=str(document.user_id),
            storage_key=document.storage_key,
            file_type=document.file_type,
        )
    except RagServiceError as exc:
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
