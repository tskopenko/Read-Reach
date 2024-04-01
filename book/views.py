from rest_framework import viewsets

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer, BookDetailSerializer


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Book objects.
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        """
        Get the list of items for this view
        """

        title = self.request.query_params.get("title")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()

    def get_serializer_class(self):
        """
        Determine which serializer class to use based on the action.
        """

        if self.action == "retrieve":
            return BookDetailSerializer

        return self.serializer_class
