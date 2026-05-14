from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import User


class ChatApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="chat@example.com",
            password="StrongPass123!",
            full_name="Chat User",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @override_settings(RAG_SERVICE_URL="http://127.0.0.1:9", RAG_TIMEOUT_SECONDS=0.05)
    def test_create_chat_and_ask_question_without_rag_service(self):
        chat = self.client.post("/api/chats/", {"title": "Contract"}, format="json")
        self.assertEqual(chat.status_code, 201)

        response = self.client.post(
            f"/api/chats/{chat.data['id']}/messages/",
            {"question": "What are the terms?", "document_ids": []},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "insufficient_context")
        self.assertEqual(response.data["citations"], [])
