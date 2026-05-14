from uuid import UUID
import hashlib

from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from chats.models import AnswerStatus, ChatMessage, ChatSession, MessageCitation, MessageRole
from core.rag_client import RagClient, RagServiceError


DEFAULT_REFUSAL = (
    "I could not find enough supporting information in your uploaded documents "
    "to answer this question."
)


def ask_question(
    *,
    chat: ChatSession,
    question: str,
    document_ids: list[UUID],
) -> dict:
    with transaction.atomic():
        ChatMessage.objects.create(
            chat_session=chat,
            role=MessageRole.USER,
            content=question,
        )
        cache_key = _answer_cache_key(
            user_id=str(chat.user_id),
            question=question,
            document_ids=document_ids,
        )
        rag_payload = cache.get(cache_key)
        cache_hit = rag_payload is not None
        if rag_payload is None:
            rag_payload = _call_rag(chat=chat, question=question, document_ids=document_ids)
            cache.set(cache_key, rag_payload, settings.ANSWER_CACHE_TTL_SECONDS)
        rag_payload["retrieval"] = {
            **rag_payload.get("retrieval", {}),
            "cache_hit": cache_hit,
        }
        assistant_message = ChatMessage.objects.create(
            chat_session=chat,
            role=MessageRole.ASSISTANT,
            content=rag_payload["answer"],
            answer_status=rag_payload["status"],
            retrieval_metadata=rag_payload["retrieval"],
        )
        citations = [
            MessageCitation.objects.create(
                message=assistant_message,
                document_id=item["document_id"],
                document_name=item["document_name"],
                chunk_id=item["chunk_id"],
                page_number=item.get("page_number"),
                score=item["score"],
                quoted_text=item["supporting_text"],
            )
            for item in rag_payload.get("citations", [])
        ]
        chat.save(update_fields=("updated_at",))

    return {
        "message_id": str(assistant_message.id),
        "status": assistant_message.answer_status,
        "answer": assistant_message.content,
        "citations": [
            {
                "document_id": str(citation.document_id),
                "document_name": citation.document_name,
                "chunk_id": str(citation.chunk_id),
                "page_number": citation.page_number,
                "score": citation.score,
                "supporting_text": citation.quoted_text,
            }
            for citation in citations
        ],
        "retrieval": assistant_message.retrieval_metadata,
    }


def _call_rag(*, chat: ChatSession, question: str, document_ids: list[UUID]) -> dict:
    try:
        payload = RagClient().ask(
            user_id=str(chat.user_id),
            chat_id=str(chat.id),
            question=question,
            document_ids=[str(document_id) for document_id in document_ids],
        )
        return _normalize_rag_payload(payload)
    except RagServiceError:
        return {
            "status": AnswerStatus.INSUFFICIENT_CONTEXT,
            "answer": DEFAULT_REFUSAL,
            "citations": [],
            "retrieval": {
                "top_k": 5,
                "threshold": 0.72,
                "cache_hit": False,
            },
        }


def _normalize_rag_payload(payload: dict) -> dict:
    status = payload.get("status", AnswerStatus.INSUFFICIENT_CONTEXT)
    if status not in AnswerStatus.values:
        status = AnswerStatus.INSUFFICIENT_CONTEXT
    return {
        "status": status,
        "answer": payload.get("answer") or DEFAULT_REFUSAL,
        "citations": payload.get("citations") or [],
        "retrieval": payload.get("retrieval")
        or {"top_k": 5, "threshold": 0.72, "cache_hit": False},
    }


def _answer_cache_key(*, user_id: str, question: str, document_ids: list[UUID]) -> str:
    question_hash = hashlib.sha256(question.strip().lower().encode("utf-8")).hexdigest()[:24]
    scope = ",".join(sorted(str(document_id) for document_id in document_ids)) or "all"
    scope_hash = hashlib.sha256(scope.encode("utf-8")).hexdigest()[:24]
    return f"answer:{user_id}:{question_hash}:{scope_hash}"
