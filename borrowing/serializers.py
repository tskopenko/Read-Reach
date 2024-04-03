from django.db import transaction
from rest_framework import serializers

from book.models import Book
from book.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book")

    def validate_book(self, value):
        if value.inventory == 0:
            raise serializers.ValidationError("Book inventory is 0")
        return value


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book",)


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
