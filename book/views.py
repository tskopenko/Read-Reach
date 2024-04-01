from rest_framework import viewsets

from book.models import Book
from book.serializers import BookSerializer, BookDetailSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):

        title = self.request.query_params.get("title")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()

    def get_serializer_class(self):

        if self.action == "retrieve":
            return BookDetailSerializer

        return self.serializer_class
