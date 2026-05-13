# API Contract

Base URL for local development: `http://localhost:8000/api`

All protected endpoints require:

```http
Authorization: Bearer <access_token>
```

## Auth

### Signup

`POST /auth/signup/`

```json
{
  "email": "user@example.com",
  "password": "strong-password",
  "full_name": "Example User"
}
```

Response:

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Example User"
}
```

### Login

`POST /auth/login/`

```json
{
  "email": "user@example.com",
  "password": "strong-password"
}
```

Response:

```json
{
  "access": "jwt-access-token",
  "refresh": "jwt-refresh-token"
}
```

### Current User

`GET /auth/me/`

## Documents

### Upload Document

`POST /documents/`

Content type: `multipart/form-data`

Fields:

- `file`: PDF, DOCX, or TXT

Response:

```json
{
  "id": "uuid",
  "filename": "contract.pdf",
  "file_type": "pdf",
  "status": "queued",
  "file_size": 123456,
  "created_at": "2026-05-12T07:15:00Z"
}
```

### List Documents

`GET /documents/`

Response:

```json
{
  "results": [
    {
      "id": "uuid",
      "filename": "contract.pdf",
      "status": "ready",
      "chunk_count": 42,
      "created_at": "2026-05-12T07:15:00Z"
    }
  ]
}
```

### Document Detail

`GET /documents/{document_id}/`

### Delete Document

`DELETE /documents/{document_id}/`

Deleting a document also deletes its chunks and invalidates related caches.

## Chats

### Create Chat Session

`POST /chats/`

```json
{
  "title": "Questions about contract"
}
```

### List Chat Sessions

`GET /chats/`

### Get Chat Session

`GET /chats/{chat_id}/`

Includes ordered message history and citations.

### Ask Question

`POST /chats/{chat_id}/messages/`

```json
{
  "question": "What are the termination conditions?",
  "document_ids": ["uuid"]
}
```

Response with sufficient context:

```json
{
  "message_id": "uuid",
  "status": "answered",
  "answer": "The agreement can be terminated with 30 days written notice, and immediately if either party materially breaches the agreement.",
  "citations": [
    {
      "document_id": "uuid",
      "document_name": "contract.pdf",
      "chunk_id": "uuid",
      "page_number": 4,
      "score": 0.87,
      "supporting_text": "Either party may terminate this Agreement upon thirty (30) days written notice..."
    }
  ],
  "retrieval": {
    "top_k": 5,
    "threshold": 0.72,
    "cache_hit": false
  }
}
```

Response with insufficient context:

```json
{
  "message_id": "uuid",
  "status": "insufficient_context",
  "answer": "I could not find enough supporting information in your uploaded documents to answer this question.",
  "citations": [],
  "retrieval": {
    "top_k": 5,
    "threshold": 0.72,
    "best_score": 0.41,
    "cache_hit": false
  }
}
```

## Dashboard

### Stats

`GET /dashboard/stats/`

Response:

```json
{
  "documents_total": 8,
  "documents_ready": 7,
  "documents_processing": 1,
  "chat_sessions": 4,
  "questions_asked": 26,
  "cache_hit_rate": 0.31
}
```

## RAG Internal Service

The FastAPI service should be private to the backend network.

### Ingest Document

`POST /internal/ingest`

```json
{
  "document_id": "uuid",
  "user_id": "uuid",
  "storage_key": "documents/user-id/document-id.pdf",
  "file_type": "pdf"
}
```

### Ask RAG

`POST /internal/ask`

```json
{
  "user_id": "uuid",
  "chat_id": "uuid",
  "question": "What are the termination conditions?",
  "document_ids": ["uuid"],
  "top_k": 5
}
```

Response shape should match the public chat answer payload so Django can store and forward it.

