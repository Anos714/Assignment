from contextlib import contextmanager
import json
from typing import Iterator
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.core.settings import settings
from app.rag.chunking import TextChunk
from app.rag.retrieval import RetrievedChunk, StoredChunk


class DatabaseNotConfigured(RuntimeError):
    pass


class Repository:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        if not self.database_url:
            raise DatabaseNotConfigured("DATABASE_URL is required for the RAG service")
        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            yield connection

    def mark_document_processing(self, document_id: UUID, user_id: UUID) -> None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE documents_document
                    SET status = 'processing', error_message = '', updated_at = NOW()
                    WHERE id = %s AND user_id = %s
                    """,
                    (document_id, user_id),
                )

    def mark_document_ready(self, document_id: UUID, user_id: UUID, chunk_count: int) -> None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE documents_document
                    SET status = 'ready', chunk_count = %s, error_message = '', updated_at = NOW()
                    WHERE id = %s AND user_id = %s
                    """,
                    (chunk_count, document_id, user_id),
                )

    def mark_document_failed(self, document_id: UUID, user_id: UUID, error_message: str) -> None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE documents_document
                    SET status = 'failed', error_message = %s, updated_at = NOW()
                    WHERE id = %s AND user_id = %s
                    """,
                    (error_message[:2000], document_id, user_id),
                )

    def replace_document_chunks(
        self,
        *,
        document_id: UUID,
        user_id: UUID,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
    ) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM documents_documentchunk WHERE document_id = %s AND user_id = %s",
                    (document_id, user_id),
                )
                for chunk, embedding in zip(chunks, embeddings, strict=True):
                    if settings.use_pgvector:
                        cursor.execute(
                            """
                            INSERT INTO documents_documentchunk
                                (id, document_id, user_id, chunk_index, page_number, content, embedding, metadata, created_at)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s::vector, %s, NOW())
                            """,
                            (
                                uuid4(),
                                document_id,
                                user_id,
                                chunk.chunk_index,
                                chunk.page_number,
                                chunk.content,
                                _vector_literal(embedding),
                                Jsonb(chunk.metadata),
                            ),
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO documents_documentchunk
                                (id, document_id, user_id, chunk_index, page_number, content, embedding, metadata, created_at)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                            """,
                            (
                                uuid4(),
                                document_id,
                                user_id,
                                chunk.chunk_index,
                                chunk.page_number,
                                chunk.content,
                                Jsonb(embedding),
                                Jsonb(chunk.metadata),
                            ),
                        )
            return len(chunks)

    def fetch_chunks(
        self,
        *,
        user_id: UUID,
        document_ids: list[UUID],
    ) -> list[StoredChunk]:
        params: list[object] = [user_id]
        document_filter = ""
        if document_ids:
            document_filter = "AND chunk.document_id = ANY(%s)"
            params.append(document_ids)

        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        chunk.id,
                        chunk.document_id,
                        doc.filename AS document_name,
                        chunk.page_number,
                        chunk.content,
                        chunk.embedding
                    FROM documents_documentchunk chunk
                    JOIN documents_document doc ON doc.id = chunk.document_id
                    WHERE chunk.user_id = %s
                    {document_filter}
                    """,
                    params,
                )
                rows = cursor.fetchall()

        return [
            StoredChunk(
                id=row["id"],
                document_id=row["document_id"],
                document_name=row["document_name"],
                page_number=row["page_number"],
                content=row["content"],
                embedding=_parse_embedding(row["embedding"]),
            )
            for row in rows
            if row["embedding"]
        ]

    def retrieve_chunks(
        self,
        *,
        user_id: UUID,
        document_ids: list[UUID],
        query_embedding: list[float],
        top_k: int,
        threshold: float,
    ) -> list[RetrievedChunk]:
        if not settings.use_pgvector:
            return []

        params: list[object] = [user_id, _vector_literal(query_embedding)]
        document_filter = ""
        if document_ids:
            document_filter = "AND chunk.document_id = ANY(%s)"
            params.append(document_ids)
        params.extend([threshold, top_k])

        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        chunk.id,
                        chunk.document_id,
                        doc.filename AS document_name,
                        chunk.page_number,
                        chunk.content,
                        chunk.embedding::text AS embedding,
                        1 - (chunk.embedding <=> %s::vector) AS score
                    FROM documents_documentchunk chunk
                    JOIN documents_document doc ON doc.id = chunk.document_id
                    WHERE chunk.user_id = %s
                    {document_filter}
                    AND 1 - (chunk.embedding <=> %s::vector) >= %s
                    ORDER BY chunk.embedding <=> %s::vector
                    LIMIT %s
                    """,
                    _pgvector_params(user_id, query_embedding, document_ids, threshold, top_k),
                )
                rows = cursor.fetchall()

        return [
            RetrievedChunk(
                chunk=StoredChunk(
                    id=row["id"],
                    document_id=row["document_id"],
                    document_name=row["document_name"],
                    page_number=row["page_number"],
                    content=row["content"],
                    embedding=_parse_embedding(row["embedding"]),
                ),
                score=float(row["score"]),
            )
            for row in rows
        ]


def _parse_embedding(value) -> list[float]:
    if isinstance(value, list):
        return [float(item) for item in value]
    if isinstance(value, str):
        vector = value.strip()
        if vector.startswith("["):
            return [float(item) for item in json.loads(vector)]
        return [float(item) for item in vector.strip("[]").split(",") if item]
    return [float(item) for item in value]


def _vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in embedding) + "]"


def _pgvector_params(
    user_id: UUID,
    query_embedding: list[float],
    document_ids: list[UUID],
    threshold: float,
    top_k: int,
) -> list[object]:
    vector = _vector_literal(query_embedding)
    params: list[object] = [vector, user_id]
    if document_ids:
        params.append(document_ids)
    params.extend([vector, threshold, vector, top_k])
    return params
