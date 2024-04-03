from datetime import date

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer
)
from payment.models import Payment
from payment.payment_utils import create_fine_session

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
        queryset = queryset.filter(user=user.id)

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

    @action(
        methods=["POST",],
        detail=True,
        url_path="return",
    )
    def return_book(self, request, pk=None):
        """
        Return a borrowed book.
        HTTP 200 OK if the book was successfully returned.
        HTTP 400 Bad Request if there is an issue returning the book or paying a fine.
        """
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            return Response(
                {"error": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if borrowing.expected_return_date.date() >= date.today():
            borrowing.actual_return_data = date.today()
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.save()

            return Response({"message": "Borrowing returned successfully."}, status=status.HTTP_200_OK)

        session = create_fine_session(borrowing, self.request)

        Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.FINE,
            borrowing=borrowing,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=session.amount_total / 100,
        )
        return Response(
            {"detail": "You must pay the fine before returning the book."},
            status=status.HTTP_400_BAD_REQUEST,
        )
