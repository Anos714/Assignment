from fastapi import APIRouter, Depends, HTTPException, status

from app.db.repository import DatabaseNotConfigured
from app.rag.service import RagService
from app.schemas import AskRequest, AskResponse, IngestRequest, IngestResponse

router = APIRouter()


async def get_rag_service() -> RagService:
    return RagService()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "rag-service"}


@router.post("/internal/ingest", response_model=IngestResponse)
async def ingest_document(
    payload: IngestRequest,
    service: RagService = Depends(get_rag_service),
):
    return service.ingest_document(payload)


@router.post("/internal/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    service: RagService = Depends(get_rag_service),
):
    try:
        return service.ask(payload)
    except DatabaseNotConfigured as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
