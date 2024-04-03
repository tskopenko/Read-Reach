import os
import stripe

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.payment_utils import stripe_card_payment
from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
    CardInformationSerializer,
)


stripe.api_key = os.environ["STRIPE_SECRET_KEY"]


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payment create, list, retrieve operations.
    """

    queryset = Payment.objects.all().select_related("borrowing")
    serializer_class = PaymentSerializer

    def get_serializer_class(self):
        """
        Determine which serializer class to use based on the action being performed.
        """
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer

        return PaymentSerializer


class PaymentAPI(APIView):
    """
    API endpoint for processing credit card payments.
    """
    serializer_class = CardInformationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            response = stripe_card_payment(data_dict=data_dict)

        else:
            response = {'errors': serializer.errors, 'status': status.HTTP_400_BAD_REQUEST}

        return Response(response)
