from rest_framework import decorators, status, viewsets
from rest_framework.response import Response

from chats.models import ChatSession
from chats.serializers import AskQuestionSerializer, ChatSessionSerializer
from chats.services import ask_question


class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        return (
            ChatSession.objects.filter(user=self.request.user)
            .prefetch_related("messages__citations")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @decorators.action(detail=True, methods=["post"], url_path="messages")
    def messages(self, request, pk=None):
        chat = self.get_object()
        serializer = AskQuestionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        payload = ask_question(
            chat=chat,
            question=serializer.validated_data["question"],
            document_ids=serializer.validated_data.get("document_ids", []),
        )
        return Response(payload, status=status.HTTP_201_CREATED)
