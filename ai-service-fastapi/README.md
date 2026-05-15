# FastAPI RAG Service

Private internal AI/RAG service for DocuMind AI. In production it runs on Render and is called by the Django backend after a document is uploaded to Cloudinary.

## Responsibilities

- Download uploaded documents from Cloudinary `secure_url` values supplied by Django.
- Fall back to local `storage_key` ingestion for local development when `file_url` is absent.
- Extract text from PDF, DOCX, and TXT files.
- Normalize and chunk document text with source metadata.
- Generate embeddings and store chunks in Neon PostgreSQL/pgvector.
- Retrieve user-scoped chunks for questions.
- Generate grounded answers with citations, using Gemini when configured.
- Cache retrieval/answer payloads with Upstash Redis when configured.

## Production Stack

- Hosting: Render
- Database: Neon PostgreSQL with `pgvector`
- Redis/cache: Upstash Redis
- File source: Cloudinary public raw `secure_url`
- LLM provider: Gemini via `LLM_PROVIDER=gemini`

FastAPI does not need Cloudinary API keys. Django owns Cloudinary upload credentials and passes the public `file_url` during ingestion.

## Environment

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST.neon.tech/DBNAME?sslmode=require
REDIS_URL=rediss://...
DOCUMENT_STORAGE_ROOT=../backend-django/media
MAX_DOCUMENT_UPLOAD_BYTES=20971520
USE_PGVECTOR=true
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-2.5-flash
```

## Ingestion

Django calls:

```http
POST /internal/ingest
```

with:

```json
{
  "document_id": "uuid",
  "user_id": "uuid",
  "filename": "contract.pdf",
  "file_url": "https://res.cloudinary.com/.../raw/upload/contract.pdf",
  "storage_key": "https://res.cloudinary.com/.../raw/upload/contract.pdf",
  "file_type": "pdf",
  "mime_type": "application/pdf"
}
```

If `file_url` exists, the service downloads the remote file into `/tmp/documindai_ingest/`, extracts/chunks/embeds it, stores chunks in Neon, then deletes the temp file. If `file_url` is missing, it resolves `storage_key` under `DOCUMENT_STORAGE_ROOT` for local development.

## Run Locally

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
