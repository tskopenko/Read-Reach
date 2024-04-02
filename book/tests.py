from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from book.serializers import BookSerializer


BOOK_URL = reverse("book:book-list")


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "Hardcover.HARD",
        "inventory": 5,
        "daily_fee": 10.00,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class UnAuthorizedTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_book_forbidden(self):
        payload = {
            "title": "Test book",
            "author": "Test author",
            "cover": "Hardcover.HARD",
            "inventory": 5,
            "daily_fee": 10.00,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class BookViewSetTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="password"
        )
        self.book = sample_book()
        self.client.force_authenticate(user=self.user)

    def test_list_books(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_book_detail(self):
        url = reverse("book:book-detail", kwargs={"pk": self.book.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_filter_by_title(self):
        book1 = sample_book(title="book_1")
        book2 = sample_book(title="book_2")

        res = self.client.get(BOOK_URL, {"title": "book_1"})

        serializer_book_1 = BookSerializer(book1)
        serializer_book_2 = BookSerializer(book2)

        self.assertIn(serializer_book_1.data, res.data)
        self.assertNotIn(serializer_book_2.data, res.data)


class AdminBookTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="password",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_create_book_by_admin(self):
        payload = {
            "title": "Test book",
            "author": "Test author",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": "10.00",
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
