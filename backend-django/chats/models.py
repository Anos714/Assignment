import uuid

from django.conf import settings
from django.db import models

from documents.models import DocumentChunk


class MessageRole(models.TextChoices):
    USER = "user", "User"
    ASSISTANT = "assistant", "Assistant"


class AnswerStatus(models.TextChoices):
    ANSWERED = "answered", "Answered"
    INSUFFICIENT_CONTEXT = "insufficient_context", "Insufficient context"


class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_sessions")
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ("-updated_at",)
        indexes = [models.Index(fields=("user", "updated_at"))]

    def __str__(self) -> str:
        return self.title


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=MessageRole.choices)
    content = models.TextField()
    answer_status = models.CharField(max_length=32, choices=AnswerStatus.choices, blank=True)
    retrieval_metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [models.Index(fields=("chat_session", "created_at"))]


class MessageCitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="citations")
    document_chunk = models.ForeignKey(
        DocumentChunk,
        on_delete=models.CASCADE,
        related_name="message_citations",
        null=True,
        blank=True,
    )
    document_id = models.UUIDField()
    document_name = models.CharField(max_length=255)
    chunk_id = models.UUIDField()
    page_number = models.PositiveIntegerField(null=True, blank=True)
    score = models.FloatField()
    quoted_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=("message",)),
            models.Index(fields=("document_chunk",)),
        ]

