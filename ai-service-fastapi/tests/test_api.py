from uuid import uuid4

import httpx
import pytest

from app.api.routes import get_rag_service
from app.core.settings import settings
from app.main import app
from app.rag.embeddings import embed_text
from app.rag.retrieval import StoredChunk
from app.rag.service import RagService


class FakeRepository:
    def fetch_chunks(self, *, user_id, document_ids):
        return [
            StoredChunk(
                id=uuid4(),
                document_id=document_ids[0],
                document_name="policy.txt",
                page_number=None,
                content="Refunds are available within fourteen days of purchase.",
                embedding=embed_text("refunds available fourteen days purchase", 384),
            )
        ]


class NullCache:
    def get_json(self, key):
        return None

    def set_json(self, key, value, ttl_seconds):
        return None


@pytest.mark.anyio
async def test_health():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.anyio
async def test_internal_ask_returns_contract_shape(monkeypatch):
    monkeypatch.setattr(settings, "retrieval_threshold", -1.0)

    async def override_rag_service():
        return RagService(repository=FakeRepository(), cache=NullCache())

    app.dependency_overrides[get_rag_service] = override_rag_service
    payload = {
        "user_id": str(uuid4()),
        "chat_id": str(uuid4()),
        "question": "What is the refund period?",
        "document_ids": [str(uuid4())],
        "top_k": 5,
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/internal/ask", json=payload)

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "answered"
    assert data["citations"][0]["document_name"] == "policy.txt"
    assert data["retrieval"]["cache_hit"] is False
