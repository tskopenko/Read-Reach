from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from django_q.tasks import async_task

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer
)

from .notificatioins import notify_new_borrowing


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

    def get_queryset(self):
        """Retrieve the movies with filters"""
        queryset = self.queryset
        user = self.request.user

        if user.is_superuser:
            user_id = self.request.query_params.get("user_id", None)
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        queryset = queryset.filter(user=user)

        is_active = self.request.query_params.get("is_active")
        if is_active:
            is_active_bool = is_active.lower() == "true"
            queryset = queryset.filter(actual_return_date__isnull=is_active_bool)

        return queryset

    def perform_create(self, serializer):
        """Perform validation book inventory is not 0 when creating a Borrowing object."""
        book = serializer.validated_data["book"]
        if book.inventory == 0:
            return Response({"error": "Book inventory is 0"}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=self.request.user)
        book.inventory -= 1
        book.save()

        async_task(notify_new_borrowing, serializer.instance.id)
