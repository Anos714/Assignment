from uuid import uuid4

from app.core.settings import settings
from app.db.repository import DatabaseNotConfigured, Repository
from app.rag.cache import Cache, retrieval_cache_key
from app.rag.chunking import chunk_pages
from app.rag.embeddings import embed_text
from app.rag.extraction import ExtractionError, extract_pages, resolve_storage_path
from app.rag.generation import DEFAULT_REFUSAL, build_grounded_answer
from app.rag.retrieval import RetrievedChunk, StoredChunk, rank_chunks
from app.schemas import AskRequest, AskResponse, IngestRequest, IngestResponse, RetrievalMetadata


class RagService:
    def __init__(self, repository: Repository | None = None, cache: Cache | None = None):
        self.repository = repository or Repository()
        self.cache = cache or Cache()

    def ingest_document(self, request: IngestRequest) -> IngestResponse:
        try:
            self.repository.mark_document_processing(request.document_id, request.user_id)
            path = resolve_storage_path(settings.document_storage_root, request.storage_key)
            pages = extract_pages(path, request.file_type)
            chunks = chunk_pages(
                pages,
                chunk_size=settings.chunk_token_size,
                overlap=settings.chunk_token_overlap,
                filename=path.name,
            )
            embeddings = [
                embed_text(chunk.content, settings.embedding_dimensions)
                for chunk in chunks
            ]
            chunk_count = self.repository.replace_document_chunks(
                document_id=request.document_id,
                user_id=request.user_id,
                chunks=chunks,
                embeddings=embeddings,
            )
            self.repository.mark_document_ready(
                request.document_id,
                request.user_id,
                chunk_count,
            )
            return IngestResponse(
                document_id=request.document_id,
                status="ready",
                chunk_count=chunk_count,
            )
        except (ExtractionError, DatabaseNotConfigured, ValueError, OSError) as exc:
            self._mark_failed_if_possible(request, str(exc))
            return IngestResponse(
                document_id=request.document_id,
                status="failed",
                chunk_count=0,
                error_message=str(exc),
            )

    def ask(self, request: AskRequest) -> AskResponse:
        key = retrieval_cache_key(
            user_id=request.user_id,
            question=request.question,
            document_ids=request.document_ids,
        )
        cached = self.cache.get_json(key)
        if cached:
            cached["retrieval"]["cache_hit"] = True
            return AskResponse(**cached)

        query_embedding = embed_text(request.question, settings.embedding_dimensions)
        retrieved = []
        if hasattr(self.repository, "retrieve_chunks"):
            retrieved = self.repository.retrieve_chunks(
                user_id=request.user_id,
                document_ids=request.document_ids,
                query_embedding=query_embedding,
                top_k=request.top_k,
                threshold=settings.retrieval_threshold,
            )
        chunks: list[StoredChunk] = []
        if not retrieved:
            chunks = self.repository.fetch_chunks(
                user_id=request.user_id,
                document_ids=request.document_ids,
            )
            retrieved = rank_chunks(
                query_embedding=query_embedding,
                chunks=chunks,
                top_k=request.top_k,
                threshold=settings.retrieval_threshold,
            )
            if not retrieved and chunks:
                retrieved = rank_chunks(
                    query_embedding=query_embedding,
                    chunks=chunks,
                    top_k=request.top_k,
                    threshold=-1.0,
                )
        answer, citations = build_grounded_answer(request.question, retrieved)
        best_score = _best_score(retrieved, chunks, query_embedding)
        status = "answered" if citations else "insufficient_context"
        response = AskResponse(
            message_id=str(uuid4()),
            status=status,
            answer=answer if citations else DEFAULT_REFUSAL,
            citations=citations,
            retrieval=RetrievalMetadata(
                top_k=request.top_k,
                threshold=settings.retrieval_threshold,
                cache_hit=False,
                best_score=best_score,
            ),
        )
        self.cache.set_json(key, response.model_dump(mode="json"), settings.retrieval_cache_ttl_seconds)
        return response

    def _mark_failed_if_possible(self, request: IngestRequest, error_message: str) -> None:
        try:
            self.repository.mark_document_failed(request.document_id, request.user_id, error_message)
        except Exception:
            return


def _best_score(
    retrieved: list[RetrievedChunk],
    chunks: list[StoredChunk],
    query_embedding: list[float],
) -> float | None:
    if retrieved:
        return round(retrieved[0].score, 4)
    if not chunks:
        return None
    ranked = rank_chunks(
        query_embedding=query_embedding,
        chunks=chunks,
        top_k=1,
        threshold=-1.0,
    )
    return round(ranked[0].score, 4) if ranked else None
