import stripe

from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

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

            stripe.api_key = "your-key-goes-here"
            response = self.stripe_card_payment(data_dict=data_dict)

        else:
            response = {
                "errors": serializer.errors,
                "status": status.HTTP_400_BAD_REQUEST,
            }

        return Response(response)

    def stripe_card_payment(self, data_dict):
        try:
            card_details = {
                "type": "card",
                "card": {
                    "number": data_dict["card_number"],
                    "exp_month": data_dict["expiry_month"],
                    "exp_year": data_dict["expiry_year"],
                    "cvc": data_dict["cvc"],
                },
            }

            payment_intent = stripe.PaymentIntent.create(
                amount=10000,
                currency="inr",
            )
            payment_intent_modified = stripe.PaymentIntent.modify(
                payment_intent["id"],
                payment_method=card_details["id"],
            )

            try:
                payment_confirm = stripe.PaymentIntent.confirm(payment_intent["id"])
                payment_intent_modified = stripe.PaymentIntent.retrieve(
                    payment_intent["id"]
                )
            except:
                payment_intent_modified = stripe.PaymentIntent.retrieve(
                    payment_intent["id"]
                )
                payment_confirm = {
                    "stripe_payment_error": "Failed",
                    "code": payment_intent_modified["last_payment_error"]["code"],
                    "message": payment_intent_modified["last_payment_error"]["message"],
                    "status": "Failed",
                }

            if (
                payment_intent_modified
                and payment_intent_modified["status"] == "succeeded"
            ):
                response = {
                    "message": "Card Payment Success",
                    "status": status.HTTP_200_OK,
                    "card_details": card_details,
                    "payment_intent": payment_intent_modified,
                    "payment_confirm": payment_confirm,
                }
            else:
                response = {
                    "message": "Card Payment Failed",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "card_details": card_details,
                    "payment_intent": payment_intent_modified,
                    "payment_confirm": payment_confirm,
                }

        except:
            response = {
                "error": "Your card number is incorrect",
                "status": status.HTTP_400_BAD_REQUEST,
                "payment_intent": {"id": "Null"},
                "payment_confirm": {"status": "Failed"},
            }
        return response


