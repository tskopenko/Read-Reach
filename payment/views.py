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

    def get_serializer_class(self):
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
