from dataclasses import dataclass
from uuid import UUID

from app.rag.embeddings import cosine_similarity


@dataclass(frozen=True)
class StoredChunk:
    id: UUID
    document_id: UUID
    document_name: str
    page_number: int | None
    content: str
    embedding: list[float]


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: StoredChunk
    score: float


def rank_chunks(
    *,
    query_embedding: list[float],
    chunks: list[StoredChunk],
    top_k: int,
    threshold: float,
) -> list[RetrievedChunk]:
    ranked = sorted(
        (
            RetrievedChunk(chunk=chunk, score=cosine_similarity(query_embedding, chunk.embedding))
            for chunk in chunks
        ),
        key=lambda item: item.score,
        reverse=True,
    )
    return [item for item in ranked[:top_k] if item.score >= threshold]

