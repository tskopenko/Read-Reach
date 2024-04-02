import os

import stripe

from django.http import HttpResponse
from rest_framework import viewsets, status
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
                return self.queryset.filter(borrowing_id__user=self.request.user)

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

            stripe.api_key = "sk_test_51P0m5x08clH0Ss5WyssxsIFAWt4DpDr3ykkBh7VdOrVRcl7rv2cCqOZZGzwX4r26TmJVs3O8oUYmWISC3bVVXDQX00sAsF15K5"
            response = stripe_card_payment(data_dict=data_dict)

        else:
            response = {
                "errors": serializer.errors,
                "status": status.HTTP_400_BAD_REQUEST,
            }

        return Response(response)



