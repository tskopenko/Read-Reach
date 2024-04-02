import os

import stripe

from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.payment_utils import stripe_card_payment
from payment.models import Payment, PaymentStatus
from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
    CardInformationSerializer,
)


stripe.api_key = "sk_test_51P0m5x08clH0Ss5WyssxsIFAWt4DpDr3ykkBh7VdOrVRcl7rv2cCqOZZGzwX4r26TmJVs3O8oUYmWISC3bVVXDQX00sAsF15K5"


class CreatePaymentAPI(APIView):
    """
    API endpoint for processing credit card payments.
    """
    serializer_class = CardInformationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            stripe_card_payment()
            return Response("Payment created successfully", status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentListView(APIView):
    """
    API endpoint for creating and listing payments.
    """
    def get(self, request):
        if not request.user.is_staff:
            # payments = Payment.objects.filter(borrowing_id__user=request.user)
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.all()

        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentDetailView(RetrieveAPIView):
    """
    API endpoint for retrieving details of a payment instance.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentDetailSerializer


class PaymentSuccessView(APIView):
    """
    API endpoint for success payment.
    """
    def get(self, request):
        try:
            session_id = request.query_params.get("session_id")
            session = stripe.checkout.Session.retrieve(session_id)
            payment = Payment.objects.get(session_id=session_id)
            payment.status = PaymentStatus.PAID.value
            payment.save()
            return HttpResponse("Payment successfully completed!")
        except stripe.error.InvalidRequestError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response("Payment not found", status=status.HTTP_404_NOT_FOUND)


class PaymentCancelView(APIView):
    """
    API endpoint for cancelling payment.
    """
    def get(self, request):
        message = (
            "Payment can be completed later"
        )
        return HttpResponse(message)
