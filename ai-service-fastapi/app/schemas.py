from uuid import UUID

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    document_id: UUID
    user_id: UUID
    filename: str | None = None
    file_url: str | None = None
    storage_key: str
    file_type: str
    mime_type: str | None = None


class IngestResponse(BaseModel):
    document_id: UUID
    status: str
    chunk_count: int
    error_message: str | None = None


class AskRequest(BaseModel):
    user_id: UUID
    chat_id: UUID
    question: str = Field(min_length=1, max_length=4000)
    document_ids: list[UUID] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)


class Citation(BaseModel):
    document_id: UUID
    document_name: str
    chunk_id: UUID
    page_number: int | None = None
    score: float
    supporting_text: str


class RetrievalMetadata(BaseModel):
    top_k: int
    threshold: float
    cache_hit: bool = False
    best_score: float | None = None


class AskResponse(BaseModel):
    message_id: str | None = None
    status: str
    answer: str
    citations: list[Citation]
    retrieval: RetrievalMetadata
