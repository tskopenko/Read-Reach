from rest_framework import viewsets
from rest_framework.views import APIView

from payment.models import Payment
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
    pass


class PaymentCancelView(APIView):
    """
    API endpoint for cancelling payment.
    """
    pass


class PaymentFineSuccessView(APIView):
    """
    API endpoint for success fine payment.
    """
    pass
