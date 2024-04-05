import os
import stripe

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
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

    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentListSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(borrowing__user=self.request.user)


class PaymentDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving details of a single payment.
    """

    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentDetailSerializer
    permission_classes = (IsAuthenticated, )


class PaymentAPI(APIView):
    """
    API endpoint for processing credit card payments.
    """

    serializer_class = CardInformationSerializer
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            response = stripe_card_payment(data_dict=data_dict)

        else:
            response = {
                "errors": serializer.errors,
                "status": status.HTTP_400_BAD_REQUEST,
            }

        return Response(response)
