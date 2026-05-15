from uuid import uuid4
from unittest.mock import Mock

from app.rag.chunking import SourcePage, chunk_pages
from app.rag.embeddings import embed_text
from app.core.settings import settings
from app.rag.generation import build_grounded_answer
from app.rag.service import RagService
from app.rag.retrieval import StoredChunk, rank_chunks
from app.schemas import AskRequest, IngestRequest


def test_chunk_pages_preserves_page_metadata():
    chunks = chunk_pages(
        [SourcePage(page_number=3, text="one two three four five six")],
        chunk_size=4,
        overlap=1,
        filename="sample.txt",
    )

    assert len(chunks) == 2
    assert chunks[0].page_number == 3
    assert chunks[0].metadata["source_filename"] == "sample.txt"


def test_embedding_retrieval_and_grounded_answer():
    document_id = uuid4()
    chunk = StoredChunk(
        id=uuid4(),
        document_id=document_id,
        document_name="contract.txt",
        page_number=1,
        content="The contract terminates after thirty days written notice. Payment is due monthly.",
        embedding=embed_text("termination thirty days written notice", 64),
    )

    retrieved = rank_chunks(
        query_embedding=embed_text("How does termination work?", 64),
        chunks=[chunk],
        top_k=1,
        threshold=-1.0,
    )
    answer, citations = build_grounded_answer("How does termination work?", retrieved)

    assert "terminates" in answer
    assert citations[0].document_id == document_id
    assert citations[0].supporting_text


def test_gemini_grounded_answer_uses_provider(monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "gemini")
    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(settings, "gemini_model", "gemini-test")

    response = Mock()
    response.read.return_value = (
        b'{"candidates":[{"content":{"parts":[{"text":"Gemini answer from context."}]}}]}'
    )
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=None)
    monkeypatch.setattr("app.rag.generation.urlopen", Mock(return_value=response))

    document_id = uuid4()
    chunk = StoredChunk(
        id=uuid4(),
        document_id=document_id,
        document_name="contract.txt",
        page_number=1,
        content="The contract terminates after thirty days written notice.",
        embedding=embed_text("termination thirty days written notice", 64),
    )
    retrieved = rank_chunks(
        query_embedding=embed_text("How does termination work?", 64),
        chunks=[chunk],
        top_k=1,
        threshold=-1.0,
    )

    answer, citations = build_grounded_answer("How does termination work?", retrieved)

    assert answer == "Gemini answer from context."
    assert citations[0].document_id == document_id


def test_ask_falls_back_to_available_chunks_when_threshold_filters_everything():
    user_id = uuid4()
    document_id = uuid4()
    chat_id = uuid4()
    chunk = StoredChunk(
        id=uuid4(),
        document_id=document_id,
        document_name="summary.txt",
        page_number=None,
        content="This file describes a project synopsis, goals, and implementation details.",
        embedding=embed_text("unrelated tokens only", 64),
    )

    class Repository:
        def retrieve_chunks(self, **kwargs):
            return []

        def fetch_chunks(self, **kwargs):
            return [chunk]

    class Cache:
        def get_json(self, key):
            return None

        def set_json(self, key, value, ttl_seconds):
            return None

    response = RagService(repository=Repository(), cache=Cache()).ask(
        AskRequest(
            user_id=user_id,
            chat_id=chat_id,
            question="Tell me about the file in brief",
            document_ids=[document_id],
            top_k=1,
        )
    )

    assert response.status == "answered"
    assert "project synopsis" in response.answer
    assert response.citations[0].document_id == document_id


def test_ingest_uses_remote_file_url_and_cleans_temp_file(monkeypatch, tmp_path):
    user_id = uuid4()
    document_id = uuid4()
    temp_file = tmp_path / "remote.txt"
    temp_file.write_text("Cloudinary text that should become one searchable chunk.")

    class Repository:
        def __init__(self):
            self.chunk_count = 0

        def mark_document_processing(self, document_id, user_id):
            return None

        def replace_document_chunks(self, *, document_id, user_id, chunks, embeddings):
            self.chunk_count = len(chunks)
            return len(chunks)

        def mark_document_ready(self, document_id, user_id, chunk_count):
            return None

    class Cache:
        def get_json(self, key):
            return None

        def set_json(self, key, value, ttl_seconds):
            return None

    repository = Repository()
    monkeypatch.setattr("app.rag.service.download_remote_file", Mock(return_value=temp_file))

    response = RagService(repository=repository, cache=Cache()).ingest_document(
        IngestRequest(
            document_id=document_id,
            user_id=user_id,
            filename="cloudinary-source.txt",
            file_url="https://res.cloudinary.com/demo/raw/upload/file.txt",
            storage_key="https://res.cloudinary.com/demo/raw/upload/file.txt",
            file_type="txt",
            mime_type="text/plain",
        )
    )

    assert response.status == "ready"
    assert response.chunk_count == 1
    assert repository.chunk_count == 1
    assert not temp_file.exists()
