# FastAPI RAG Service

Private internal service for document ingestion and grounded retrieval.

## Responsibilities

- Extract text from PDF, DOCX, and TXT files saved by Django.
- Normalize and chunk document text with source metadata.
- Generate deterministic local embeddings for assignment/local development.
- Store chunks and embeddings in the Django `documents_documentchunk` table.
- Retrieve user-scoped chunks for questions.
- Return grounded answers with citations, or `insufficient_context` when evidence is weak.
- Optionally cache retrieval/answer payloads in Redis.

## Environment

Copy `.env.example` to `.env` and use the same Neon database URL as Django:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST.neon.tech/DBNAME?sslmode=require
DOCUMENT_STORAGE_ROOT=../backend-django/media
REDIS_URL=redis://localhost:6379/0
```

For Gemini-backed answers, keep the key in `.env` and set:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-2.5-flash
```

## Run

```bash
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

## Test

```bash
.venv/bin/python -m pytest
```

## Internal Endpoints

- `GET /health`
- `POST /internal/ingest`
- `POST /internal/ask`
