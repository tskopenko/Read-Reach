from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing


BORROWING_URL = reverse("borrowing:borrowing-list")


def sample_borrowing(**params):
    book = params.get("book")
    if book:
        book.inventory -= 1
        book.save()

    defaults = {
        "borrow_date": "2024-04-02",
        "expected_return_date": "2024-04-08",
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


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


class BorrowingViewSetTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="password",
        )
        self.book = sample_book()
        self.client.force_authenticate(self.user)

    def test_create_borrowing(self):
        borrowing = sample_borrowing(book=self.book, user=self.user)

        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(self.book.inventory, 4)

    def test_perform_create_book_inventory_zero(self):
        self.book.inventory = 0
        self.book.save()

        url = BORROWING_URL
        data = {"book": self.book}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Borrowing.objects.count(), 0)
        self.assertEqual(self.book.inventory, 0)

    def test_get_queryset_user_filter_user_id(self):
        borrowing = sample_borrowing(
            user=self.user,
            expected_return_date="2024-04-08",
            actual_return_date=None,
            book=self.book,
        )

        url = BORROWING_URL
        data = {"user": self.user}
        self.client.force_authenticate(self.user)
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], borrowing.id)

    def test_get_queryset_user_filter_user_id_with_other_user(self):
        borrowing = sample_borrowing(
            user=self.user,
            expected_return_date="2024-04-08",
            actual_return_date=None,
            book=self.book,
        )
        other_user = get_user_model().objects.create(
            email="other@example.com",
            password="password",
        )

        url = BORROWING_URL
        data = {"user": other_user.id}
        self.client.force_authenticate(other_user)
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_queryset_active_filter(self):
        borrowing = sample_borrowing(
            user=self.user,
            expected_return_date="2024-04-08",
            actual_return_date=None,
            book=self.book,
        )

        url = BORROWING_URL
        data = {"is_active": "true"}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], borrowing.id)

    def test_get_queryset_not_active_filter(self):
        borrowing = sample_borrowing(
            user=self.user,
            expected_return_date="2024-04-08",
            actual_return_date="2024-04-07",
            book=self.book,
        )

        url = BORROWING_URL
        data = {"is_active": "false"}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], borrowing.id)


class ReturnBookTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="password",
        )
        self.book = sample_book(
            title="Sample book",
            author="Sample author",
            cover="Hardcover.HARD",
            inventory=5,
            daily_fee=10.00,
        )
        self.client.force_authenticate(self.user)

    def test_return_book_success(self):
        borrowing = sample_borrowing(
            user=self.user,
            book=self.book,
            expected_return_date="2024-04-08",
            actual_return_date=None,
        )
        url = reverse("borrowing:borrowing-return-book", kwargs={"pk": borrowing.id})
        data = {"actual_return_date": "2024-04-07"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Borrowing returned successfully.")

    def test_return_book_already_returned(self):
        borrowing = sample_borrowing(
            user=self.user,
            book=self.book,
            actual_return_date="2024-04-06",
        )
        url = reverse("borrowing:borrowing-return-book", kwargs={"pk": borrowing.id})
        print(url)
        data = {"actual_return_date": "2024-04-07"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "This borrowing has already been returned."
        )
        # Ensure borrowing and book inventory remain unchanged
        borrowing.refresh_from_db()
        expected_return_date = datetime.strptime("2024-04-06", "%Y-%m-%d").date()

        self.assertEqual(borrowing.actual_return_date.date(), expected_return_date)
        self.assertEqual(self.book.inventory, 4)
