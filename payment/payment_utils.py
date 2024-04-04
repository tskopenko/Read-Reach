import os
import datetime
from decimal import Decimal

import stripe

from rest_framework import serializers
from rest_framework import status
from stripe import InvalidRequestError

from payment.models import Payment
from borrowing.models import Borrowing


stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
LOCAL_DOMAIN = "http://127.0.0.1:8000/"
FINE_MULTIPLIER = 2
SUCCESS_URL = "https://example.com/success"
CANCEL_URL = "https://example.com/cancel"


def create_payment() -> None:
    pass


def create_checkout_session(borrowing, money_to_pay):
    """
    Function to create a checkout session for Stripe payment.

    This function creates a checkout session for a Stripe payment based on
    the provided borrowing information and amount to pay.

    Args:
        borrowing (Borrowing): The borrowing object associated with the payment.
        money_to_pay (int): The amount to pay in cents.

    Returns:
        dict: A dictionary representing the created checkout session.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": money_to_pay,
                    "product_data": {
                        "name": borrowing.book.title,
                        "description": f"Author: {borrowing.book.author}",
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=SUCCESS_URL,
        cancel_url=CANCEL_URL,
    )
    return session


def set_status_paid(payment):
    """
    Function to set the status of a payment to 'PAID'.

    Args:
        payment (Payment): The payment object whose status needs to be updated.

    Returns:
        None
    """
    payment.status = Payment.StatusChoices.PAID.value
    payment.save()


def stripe_card_payment(data_dict):
    """
    Function to process card payment using Stripe API.

    This function takes in a dictionary containing payment information,
    such as amount, borrowing ID, and payment type. It then creates a Stripe
    payment intent, creates a payment object in the database, and returns
    a response with payment details.

    Args:
        data_dict (dict): A dictionary containing payment information,
                          including amount, borrowing ID, and payment type.

    Returns:
        dict: A dictionary containing payment details or error information.
    """
    try:
        amount = float(data_dict.get("amount", 0))
        amount_in_cents = int(amount * 100)
        borrowing_id = data_dict.get("borrowing")
        borrowing = Borrowing.objects.get(id=borrowing_id)
        type_status = data_dict.get("type")

        session = create_checkout_session(borrowing, amount_in_cents)

        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="usd",
            payment_method="pm_card_visa_debit",
            confirm=True,
            confirmation_method="manual",
            return_url=SUCCESS_URL,
        )

        if payment_intent.status == "succeeded":

            payment = Payment.objects.create(
                borrowing=borrowing,
                session_url=session.url,
                session_id=session.id,
                type=type_status.upper(),
                status=Payment.StatusChoices.PENDING.value,
                money_to_pay=amount,
            )

            response = {
                "payment_id": payment.id,
                "status": status.HTTP_200_OK,
                "message": "Payment successfully completed!",
                "user": payment.borrowing.user.email,
                "amount": amount,
                "session_url": session.url,
                "session_id": session.id,
            }

            set_status_paid(payment)

        else:
            response = {
                "message": "Card Payment Failed",
                "status": status.HTTP_400_BAD_REQUEST,
                "payment_intent": payment_intent,
                "session_url": session.url,
                "session_id": session.id,
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
