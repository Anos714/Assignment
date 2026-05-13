# AI-Powered Knowledge Base Assistant

Production-oriented full-stack RAG assignment for uploading documents, asking questions over private knowledge bases, and returning grounded answers with citations.

## Planned Stack

- Frontend: React.js, Tailwind CSS
- API backend: Django, Django REST Framework
- AI service: FastAPI
- Database: PostgreSQL with `pgvector`
- Cache and queue broker: Redis
- Background workers: Celery
- Object storage: local development storage, S3/GCS ready
- Containerization: Docker Compose for local development

## Core Services

- `frontend`: user interface for auth, uploads, dashboard, and chat
- `django-api`: authentication, document metadata, chat history, dashboard APIs
- `rag-service`: extraction, chunking, embeddings, retrieval, and grounded generation
- `worker`: async ingestion jobs for parsing and embedding documents
- `postgres`: relational data plus vector index
- `redis`: caching, rate limiting, Celery broker/result backend

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Contract](docs/API.md)

## Build Phases

1. Scaffold Django, FastAPI, React, PostgreSQL, Redis, and Docker Compose.
2. Implement authentication and protected APIs.
3. Add document upload, validation, metadata tracking, and async ingestion.
4. Build extraction, chunking, embedding, vector storage, and retrieval.
5. Add grounded answer generation with strict citation validation.
6. Build chat UI, citation display, dashboard stats, and history.
7. Add caching, tests, API docs, and deployment notes.

