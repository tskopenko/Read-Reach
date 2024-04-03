from datetime import date

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowing.models import Borrowing
from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payment create, list, retrieve operations.
    """
    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentSerializer

    # def get_queryset(self):
    #     """
    #     For admin-user return all payments;
    #     For simple user return only payments related to the current user
    #     """
    #     if self.action == "list":
    #         if not self.request.user.is_staff:
    #             return self.queryset.filter(borrowing_id__user=self.request.user)
    #
    #     return self.queryset

    def get_serializer_class(self):
        """
        Determine which serializer class to use based on the action being performed.
        """
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer


class PaymentSuccessView(APIView):
    """
    API endpoint for success payment.
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="pk",
                description="ID of the borrowing object",
                type=int,
            ),
        ],
    )
    def get(self, request, pk):
        """
        Process successful payment.

        Parameters:
        - pk (int): ID of the borrowing object.

        Returns:
        - HTTP 200 OK: Payment successfully processed!
        """
        borrowing = Borrowing.objects.get(id=pk)
        payment = Payment.objects.get(borrowing=borrowing)
        payment.status = Payment.StatusChoices.PAID
        payment.money_to_pay = 0
        payment.save()
        return Response(
            {"message": "Payment successfully processed!"},
            status=status.HTTP_200_OK,
        )


class PaymentFineSuccessView(APIView):
    """
    API endpoint for success fine payment.
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="pk",
                description="ID of the borrowing object",
                type=int,
            ),
        ],
    )
    def get(self, request, pk):
        """
        Process successful fine payment.

        Parameters:
        - pk (int): ID of the borrowing object.

        Returns:
        - HTTP 200 OK: Payment fine was successfully processed.
        """
        borrowing = Borrowing.objects.get(id=pk)
        payment = Payment.objects.get(
            borrowing=borrowing, type=Payment.TypeChoices.FINE
        )
        payment.status = Payment.StatusChoices.PAID
        payment.money_to_pay = 0
        payment.save()

        borrowing.actual_return_data = date.today()
        borrowing.book.inventory += 1
        borrowing.book.save()
        borrowing.save()
        return Response(
            {"message": "Payment fine was successfully processed"},
            status=status.HTTP_200_OK,
        )


class PaymentCancelView(APIView):
    """
    API endpoint for cancelling payment.
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="pk",
                description="ID of the payment",
                type=int,
            ),
        ],
    )
    def get(self, request, pk):
        """
        Cancel payment.

        Parameters:
        - pk (int): ID of the payment.

        Returns:
        - HTTP 400 Bad Request: Payment can be completed later. Please note that the session will remain active for 24 hours.
        """
        return Response(
            {
                "message":
                    "Payment can be completed later.\n"
                    "Please note that the session will remain active for 24 hours."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
