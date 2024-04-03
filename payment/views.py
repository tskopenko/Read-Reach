import os
import stripe

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.payment_utils import stripe_card_payment
from payment.models import Payment
from payment.serializers import (
    CardInformationSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer,
)


stripe.api_key = os.environ["STRIPE_SECRET_KEY"]


class PaymentListAPIView(generics.ListAPIView):
    """
    API endpoint for retrieving a list of payments.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentListSerializer


class PaymentDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving details of a single payment.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentDetailSerializer


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
