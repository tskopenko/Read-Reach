import os
import datetime

import stripe

from rest_framework import serializers
from rest_framework import status
from stripe import InvalidRequestError

from payment.models import Payment
from borrowing.models import Borrowing


stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
LOCAL_DOMAIN = "http://127.0.0.1:8000/"
FINE_MULTIPLIER = 2


def stripe_card_payment(data_dict):
    try:
        amount = float(data_dict.get("amount", 0))
        amount_in_cents = int(amount * 100)

        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="usd",
            payment_method="pm_card_visa_debit",
            confirm=True,
            confirmation_method="manual",
            return_url=f"{LOCAL_DOMAIN}api/payments/success_payment",  # NO EFFECT.fix later
        )

        if payment_intent.status == "succeeded":

            payment = Payment.objects.create(
                borrowing=Borrowing.objects.get(id=1),
                session_url="https://example.com/session",
                session_id="123459789",
                type=Payment.TypeChoices.PAYMENT.value,
                status=Payment.StatusChoices.PAID.value,
                money_to_pay=amount,
            )

            response = {
                "payment_id": payment.id,
                "status": status.HTTP_200_OK,
                "message": "Payment successfully completed!",
                "user": payment.borrowing.user.email,
                "amount": amount,
            }
        else:
            response = {
                "message": "Card Payment Failed",
                "status": status.HTTP_400_BAD_REQUEST,
                "payment_intent": payment_intent,
            }

    except InvalidRequestError:
        response = {
            "error": "Payment amounts must be positive integers, equal to or greater than 1.",
            "status": status.HTTP_400_BAD_REQUEST,
        }

    except stripe.error.CardError as e:
        # Handle card error (e.g., invalid card number, expired card)
        response = {
            "error": str(e),
            "status": status.HTTP_400_BAD_REQUEST,
        }

    return response


def check_expiry_month(value):
    """
    Check if the provided expiry month is valid.
    Raises a validation error if the month is not between 1 and 12.
    """
    if not 1 <= int(value) <= 12:
        raise serializers.ValidationError("Invalid expiry month.")


def check_expiry_year(value):
    """
    Check if the provided expiry year is valid.
    Raises a validation error if the year is not greater than or equal to the current year.
    """
    today = datetime.datetime.now()
    if not int(value) >= today.year:
        raise serializers.ValidationError("Invalid expiry year.")


def check_cvc(value):
    """
    Check if the provided CVC number is valid.
    Raises a validation error if the length of the CVC number is not between 3 and 4 characters.
    """
    if not 3 <= len(value) <= 4:
        raise serializers.ValidationError("Invalid CVC number.")


def check_payment_method(value):
    """
    Check if the provided payment method is valid.
    Raises a validation error if the payment method is not 'card'.
    """
    payment_method = value.lower()
    if payment_method not in ["card"]:
        raise serializers.ValidationError("Invalid payment method.")
