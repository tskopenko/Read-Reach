from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import Payment, PaymentStatus, PaymentType
from borrowing.models import Borrowing
from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer
)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payment create, list, retrieve operations.
    """
    queryset = Payment.objects.all().select_related("borrowing")
    serializer_class = PaymentSerializer

    def get_queryset(self):
        """
        For admin-user return all payments;
        For simple user return only payments related to the current user
        """
        if self.action == "list":
            if not self.request.user.is_staff:
                return self.queryset.filter(
                    borrowing_id__user=self.request.user
                )

        return self.queryset

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

    def post(self, request, pk):
        borrowing = Borrowing.objects.get(id=pk)
        try:
            payment = Payment.objects.get(borrowing=borrowing)
            payment.status = PaymentStatus.PAID.value
            payment.type = PaymentType.PAYMENT.value
            payment.money_to_pay = 0
            payment.save()
            return Response("Payment successful", status=status.HTTP_200_OK)

        except Borrowing.DoesNotExist:
            return Response("Borrowing not found", status=status.HTTP_404_NOT_FOUND)
        except Payment.DoesNotExist:
            return Response("Payment not found", status=status.HTTP_404_NOT_FOUND)


class PaymentCancelView(APIView):
    """
    API endpoint for cancelling payment.
    """
    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        payment.delete()
        return Response("Payment cancelled", status=status.HTTP_200_OK)


class PaymentFineSuccessView(APIView):
    """
    API endpoint for success fine payment.
    """
    pass

