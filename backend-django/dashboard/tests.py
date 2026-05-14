from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User


class DashboardApiTests(TestCase):
    def test_stats_requires_authentication(self):
        response = APIClient().get("/api/dashboard/stats/")
        self.assertEqual(response.status_code, 401)

    def test_stats_shape(self):
        user = User.objects.create_user(
            email="stats@example.com",
            password="StrongPass123!",
            full_name="Stats User",
        )
        client = APIClient()
        client.force_authenticate(user)

        response = client.get("/api/dashboard/stats/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.data),
            {
                "documents_total",
                "documents_ready",
                "documents_processing",
                "chat_sessions",
                "questions_asked",
                "cache_hit_rate",
            },
        )
