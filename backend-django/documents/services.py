from threading import Thread

from django.conf import settings

from documents.models import Document, DocumentStatus
from documents.tasks import ingest_document_task


def enqueue_document_ingestion(document: Document) -> None:
    document.status = DocumentStatus.QUEUED
    document.save(update_fields=("status", "updated_at"))
    if settings.CELERY_TASK_ALWAYS_EAGER:
        Thread(
            target=_run_ingestion_in_background,
            args=(str(document.id),),
            daemon=True,
        ).start()
        return
    try:
        ingest_document_task.delay(str(document.id))
    except Exception as exc:
        document.error_message = f"Could not enqueue ingestion job: {exc}"[:2000]
        document.save(update_fields=("error_message", "updated_at"))


def _run_ingestion_in_background(document_id: str) -> None:
    try:
        ingest_document_task(document_id)
    except Exception:
        return
