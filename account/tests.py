from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class AccountAPITestCase(APITestCase):

    def setUp(self):
        """Create a test user for authentication"""
        self.user = User.objects.create_user(username="testuser", password="testpassword")

    def test_register_user(self):
        """Test user registration"""
        data = {
            "username": "newuser",
            "password": "newpassword"
        }
        response = self.client.post("/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)

    def test_login_user(self):
        """Test user login and token retrieval"""
        data = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = self.client.post("/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)  # Ensure JWT access token is received
        self.access_token = response.data["access"]

    def test_protected_route_requires_authentication(self):
        """Test that accessing a protected route without authentication fails"""
        response = self.client.get("/blog/posts/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_route_with_token(self):
        """Test accessing a protected route with a valid token"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get("/blog/posts/")
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_user(self):
        """Test user logout by revoking refresh token"""
        refresh = RefreshToken.for_user(self.user)
        refresh_token = str(refresh)

        data = {"refresh": refresh_token}
        response = self.client.post("/logout/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
