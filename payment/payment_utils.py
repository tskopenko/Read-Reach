import os
import datetime
import stripe

from rest_framework import serializers
from rest_framework import status



# stripe.api_key = "sk_test_51P0m5x08clH0Ss5WyssxsIFAWt4DpDr3ykkBh7VdOrVRcl7rv2cCqOZZGzwX4r26TmJVs3O8oUYmWISC3bVVXDQX00sAsF15K5"
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
LOCAL_DOMAIN = "http://127.0.0.1:8000/"
FINE_MULTIPLIER = 2


def stripe_card_payment(data_dict):
    try:
        # Create a payment intent with the specified amount, currency, and payment method
        payment_intent = stripe.PaymentIntent.create(
            amount=10000,
            currency="inr",
            payment_method="pm_card_visa_debit",
            confirm=True,
            confirmation_method="manual",
            return_url=f"{LOCAL_DOMAIN}api/payments/success_payment",
        )

        if payment_intent.status == "succeeded":
            response = {
                "message": "Payment successfully completed!",
                "status": status.HTTP_200_OK,
                "payment_intent": payment_intent,
            }
        else:
            response = {
                "message": "Card Payment Failed",
                "status": status.HTTP_400_BAD_REQUEST,
                "payment_intent": payment_intent,
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
