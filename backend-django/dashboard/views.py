from rest_framework.response import Response
from rest_framework.views import APIView

from chats.models import ChatMessage, ChatSession, MessageRole
from documents.models import Document, DocumentStatus


class DashboardStatsView(APIView):
    def get(self, request):
        documents = Document.objects.filter(user=request.user)
        chat_sessions = ChatSession.objects.filter(user=request.user)
        questions = ChatMessage.objects.filter(
            chat_session__user=request.user,
            role=MessageRole.USER,
        )
        return Response(
            {
                "documents_total": documents.count(),
                "documents_ready": documents.filter(status=DocumentStatus.READY).count(),
                "documents_processing": documents.filter(
                    status__in=[DocumentStatus.QUEUED, DocumentStatus.PROCESSING]
                ).count(),
                "chat_sessions": chat_sessions.count(),
                "questions_asked": questions.count(),
                "cache_hit_rate": 0.0,
            }
        )

