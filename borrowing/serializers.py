from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", )


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


class CreateBorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "book")

    def validate_book(self, value):
        if value.inventory == 0:
            raise serializers.ValidationError("Book inventory is 0")
        return value

    def create(self, validated_data):
        book = validated_data.get("book")

        if book.inventory == 0:
            raise serializers.ValidationError("Book inventory is 0")

        borrowing = Borrowing.objects.create(
            borrow_date=validated_data["borrow_date"],
            expected_return_date=validated_data["expected_return_date"],
            book=book,
        )
        book.inventory -= 1
        book.save()
        return borrowing
