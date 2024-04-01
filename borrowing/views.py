from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet for managing Borrowing objects."""

    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        """Determine which serializer class to use based on the action."""
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Perform validation book inventory is not 0 when creating a Borrowing object."""
        book = serializer.validated_data["book"]
        if book.inventory == 0:
            return Response({"error": "Book inventory is 0"}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=self.request.user)
        book.inventory -= 1
        book.save()
