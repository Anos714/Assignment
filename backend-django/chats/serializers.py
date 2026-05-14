from rest_framework import serializers

from chats.models import ChatMessage, ChatSession, MessageCitation
from documents.models import Document


class CitationSerializer(serializers.ModelSerializer):
    supporting_text = serializers.CharField(source="quoted_text")

    class Meta:
        model = MessageCitation
        fields = (
            "document_id",
            "document_name",
            "chunk_id",
            "page_number",
            "score",
            "supporting_text",
        )


class ChatMessageSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="answer_status", allow_blank=True)
    citations = CitationSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = ("id", "role", "content", "status", "citations", "created_at")


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ("id", "title", "created_at", "updated_at", "messages")
        read_only_fields = ("id", "created_at", "updated_at", "messages")


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=4000)
    document_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
    )

    def validate_document_ids(self, value):
        user = self.context["request"].user
        existing = set(
            Document.objects.filter(user=user, id__in=value).values_list("id", flat=True)
        )
        missing = [str(document_id) for document_id in value if document_id not in existing]
        if missing:
            raise serializers.ValidationError("One or more documents do not exist.")
        return value

