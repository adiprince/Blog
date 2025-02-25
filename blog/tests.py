from django.test import TestCase
from your_app.serializers import BlogPostSerializer
from your_app.models import BlogPost
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken


class BlogPostModelTest(TestCase):
    def setUp(self):
        self.blog = BlogPost.objects.create(title="Test Blog", content="This is a test blog.")

    def test_blog_creation(self):
        self.assertEqual(self.blog.title, "Test Blog")
        self.assertEqual(self.blog.content, "This is a test blog.")

class BlogPostSerializerTest(TestCase):
    def setUp(self):
        self.blog_data = {"title": "Test Blog", "content": "This is a test blog."}
        self.blog = BlogPost.objects.create(**self.blog_data)
        self.serializer = BlogPostSerializer(instance=self.blog)

    def test_serializer_data(self):
        data = self.serializer.data
        self.assertEqual(data["title"], self.blog_data["title"])
        self.assertEqual(data["content"], self.blog_data["content"])

class BlogPostAPITest(APITestCase):
    def setUp(self):
        self.blog = BlogPost.objects.create(title="Test Blog", content="This is a test blog.")
        self.list_url = reverse("blog-list")  # URL name from your urls.py
        self.detail_url = reverse("blog-detail", kwargs={"pk": self.blog.pk})

    def test_get_blog_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_blog_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Blog")

    def test_create_blog(self):
        data = {"title": "New Blog", "content": "This is a new test blog."}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogPost.objects.count(), 2)

    def test_update_blog(self):
        data = {"title": "Updated Blog", "content": "Updated content."}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, "Updated Blog")

    def test_delete_blog(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BlogPost.objects.count(), 0)

class BlogPostFilterAPITestCase(APITestCase):

    def setUp(self):
        """Set up test data: users and blog posts"""
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")

        # Get JWT token for authentication
        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create blog posts with different dates & users
        self.post1 = BlogPost.objects.create(
            title="User1 Post Today",
            content="Post by user1 today",
            author=self.user1,
            created_at=datetime.now()
        )
        self.post2 = BlogPost.objects.create(
            title="User1 Post Yesterday",
            content="Post by user1 yesterday",
            author=self.user1,
            created_at=datetime.now() - timedelta(days=1)
        )
        self.post3 = BlogPost.objects.create(
            title="User2 Post Today",
            content="Post by user2 today",
            author=self.user2,
            created_at=datetime.now()
        )

    def test_filter_by_user(self):
        """Test filtering blog posts by user ID"""
        response = self.client.get(f"/blog/posts/filter/?author={self.user1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # User1 has 2 posts

    def test_filter_by_date(self):
        """Test filtering blog posts by date"""
        today = datetime.now().date()
        response = self.client.get(f"/blog/posts/filter/?date={today}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 2 posts created today

    def test_filter_by_user_and_date(self):
        """Test filtering blog posts by both user and date"""
        today = datetime.now().date()
        response = self.client.get(f"/blog/posts/filter/?author={self.user1.id}&date={today}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only 1 post by user1 today

    def test_filter_no_results(self):
        """Test filtering with no matching posts"""
        response = self.client.get("/blog/posts/filter/?author=9999")  # Non-existent user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should return an empty list
