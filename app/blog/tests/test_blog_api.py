"""Test to test log api"""

from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from blog.models import Blogs

LOGIN_URL = reverse("user:login")
CREATE_BLOG = reverse("blog:create")
LIKE_BLOG = reverse("blog:like")


def get_manage_blog_url(blog_id):
    return reverse("blog:manage", args=[blog_id])


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class TestBlogAPI(TestCase):

    def setUp(self):
        paylaod = {
            "email": "test@example.com",
            "password": "testpass123",
            "username": "testuser",
            "name": "Test Name",
        }
        self.user = create_user(**paylaod)
        self.client = APIClient()

        res = self.client.post(LOGIN_URL, paylaod)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {res.data["access"]}')

    def test_blog_creation(self):
        payload = {"title": "first blog", "text": "text"}
        res = self.client.post(CREATE_BLOG, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)

    def test_blog_retrive(self):

        data = {"title": "first blog", "text": "text"}
        blog = Blogs.objects.create(user=self.user, **data)

        res = self.client.get(get_manage_blog_url(blog_id=blog.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("id", res.data)

    def test_update_blog_retrive(self):
        data = {"title": "first blog", "text": "text"}
        update_data = {"title": "update first blog", "text": "new text"}
        blog = Blogs.objects.create(user=self.user, **data)

        res = self.client.patch(get_manage_blog_url(blog_id=blog.id), update_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], update_data["title"])

    def test_like_blog(self):
        data = {"title": "first blog", "text": "text"}
        blog = Blogs.objects.create(user=self.user, **data)
        blog_data = {"blog_id": blog.id}
        res = self.client.post(LIKE_BLOG, blog_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.delete(LIKE_BLOG, blog_data)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
