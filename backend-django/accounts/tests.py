from django.test import TestCase
from rest_framework.test import APIClient


class AuthApiTests(TestCase):
    def test_signup_login_and_me(self):
        client = APIClient()

        signup = client.post(
            "/api/auth/signup/",
            {
                "email": "person@example.com",
                "password": "StrongPass123!",
                "full_name": "Person Example",
            },
            format="json",
        )
        self.assertEqual(signup.status_code, 201)
        self.assertEqual(signup.data["email"], "person@example.com")

        login = client.post(
            "/api/auth/login/",
            {"email": "person@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(login.status_code, 200)
        self.assertIn("access", login.data)

        client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        me = client.get("/api/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["full_name"], "Person Example")

