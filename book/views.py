from rest_framework import viewsets

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer


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
