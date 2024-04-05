from rest_framework import serializers

from book.models import Book, CoverType


class BookSerializer(serializers.ModelSerializer):
    cover = serializers.ChoiceField(choices=[(tag.name, tag.value) for tag in CoverType])

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee",)
