# DocuMind AI

DocuMind AI is a full-stack RAG web app for uploading PDF, DOCX, and TXT documents, asking questions over private document collections, and receiving grounded answers with citations.

## Deployed Stack

- Frontend: React, Vite, Tailwind CSS, deployed on Vercel
- Django backend: Django REST Framework API, deployed on Render
- AI/RAG service: FastAPI, deployed on Render
- Database: Neon PostgreSQL with `pgvector`
- Redis: Upstash Redis for cache and Celery broker/result backend
- File storage: Cloudinary raw uploads for shared document storage
- LLM: Gemini-backed generation, with extractive fallback behavior

## Core Services

- `frontend`: landing page, auth UI, uploads, dashboard, sidebar stats, chat, citations
- `backend-django`: authentication, document metadata, Cloudinary upload, chat history, dashboard APIs
- `ai-service-fastapi`: Cloudinary file download, extraction, chunking, embeddings, retrieval, answer generation
- Neon: relational data plus vector storage for `documents_documentchunk.embedding`
- Upstash Redis: retrieval/answer cache and task infrastructure
- Cloudinary: stores original uploaded PDF/DOCX/TXT files as public raw assets

## Document Flow

1. User uploads a document from the Vercel frontend.
2. Django validates file type and size.
3. Django uploads the original file to Cloudinary using `resource_type="raw"`, `type="upload"`, and `access_mode="public"`.
4. Django stores Cloudinary metadata on `Document`, including `cloudinary_secure_url`.
5. Django queues ingestion and sends `file_url=cloudinary_secure_url` to the FastAPI RAG service.
6. FastAPI downloads the file from Cloudinary into `/tmp/documindai_ingest/`.
7. FastAPI extracts text, chunks it, embeds it, and stores chunks/vectors in Neon.
8. Django marks the document `ready` with `chunk_count > 0`.
9. Chat retrieval uses the stored chunks and returns grounded answers with citations.

Local development still supports the older local `storage_key` ingestion path when Cloudinary is not configured.

## Deployment Notes

### Vercel Frontend

Set frontend environment variables to point at the deployed Django API if needed:

```env
VITE_API_BASE_URL=https://your-django-render-service.onrender.com/api
VITE_RAG_BASE_URL=/rag
```

The frontend never receives Cloudinary API secrets.

### Render Django Backend

Required environment variables include:

```env
DATABASE_URL=postgresql://...
REDIS_URL=rediss://...
CELERY_BROKER_URL=rediss://...
CELERY_RESULT_BACKEND=rediss://...
RAG_SERVICE_URL=https://your-fastapi-render-service.onrender.com
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
MAX_DOCUMENT_UPLOAD_BYTES=20971520
USE_PGVECTOR=true
```

Recommended Render build command:

```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

### Render FastAPI RAG Service

Required environment variables include:

```env
DATABASE_URL=postgresql://...
REDIS_URL=rediss://...
DOCUMENT_STORAGE_ROOT=../backend-django/media
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
USE_PGVECTOR=true
MAX_DOCUMENT_UPLOAD_BYTES=20971520
```

FastAPI does not need Cloudinary API keys because it downloads from Django's stored `cloudinary_secure_url`.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Contract](docs/API.md)
- [FastAPI RAG Service](ai-service-fastapi/README.md)
