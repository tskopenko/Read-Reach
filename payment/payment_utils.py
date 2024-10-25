import datetime

import stripe
from stripe import InvalidRequestError

from rest_framework import serializers
from rest_framework import status

from django.conf import settings

from payment.models import Payment
from borrowing.models import Borrowing


stripe.api_key = settings.STRIPE_SECRET_KEY
LOCAL_DOMAIN = settings.LOCAL_DOMAIN
FINE_MULTIPLIER = 2
SUCCESS_URL = "https://example.com/success"
CANCEL_URL = "https://example.com/cancel"


def count_amount_to_pay(borrowing):
    """
    Function to handle the returning of a borrowed book.
    """
    actual_return_data = datetime.date.today()
    expected_return_date = borrowing.expected_return_date.date()
    borrowing.actual_return_date = actual_return_data
    borrowing.save()

    if actual_return_data <= expected_return_date:
        borrowed_days = borrowing.expected_return_date - borrowing.borrow_date
        amount_to_pay = borrowed_days.days * borrowing.book.daily_fee

    else:
        overdue_days = (actual_return_data - expected_return_date).days
        amount_to_pay = overdue_days * borrowing.book.daily_fee * FINE_MULTIPLIER

    if amount_to_pay > 0:
        return amount_to_pay

    return borrowing.book.daily_fee


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


def set_type(payment, borrowing):
    """
    Function to set the type of payment based on the borrowing details.
    """
    if datetime.date.today() <= borrowing.expected_return_date.date():
        payment.type = Payment.TypeChoices.PAYMENT.value
    else:
        payment.type = Payment.TypeChoices.FINE.value


def set_status(payment):
    """
    Function to set the status of payment based on the payment details.
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
    borrowing_id = data_dict.get("borrowing")
    borrowing = Borrowing.objects.get(id=borrowing_id)

    amount = count_amount_to_pay(borrowing)
    amount_in_cents = int(amount * 100)

    session = create_checkout_session(borrowing, amount_in_cents)

    try:
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
                type=Payment.TypeChoices.FINE.value,
                status=Payment.StatusChoices.PENDING.value,
                money_to_pay=amount,
            )

            set_status(payment)
            set_type(payment, borrowing)

            response = {
                "payment_id": payment.id,
                "status": status.HTTP_200_OK,
                "message": "Payment successfully completed!",
                "user": payment.borrowing.user.email,
                "amount": amount,
                "type": payment.type,
                "session_url": session.url,
                "session_id": session.id,
            }

        else:
            response = {
                "message": "Card Payment Failed",
                "status": status.HTTP_400_BAD_REQUEST,
                "payment_intent": payment_intent,
                "session_url": session.url,
                "session_id": session.id,
            }

    except InvalidRequestError as error:
        response = {
            "error": str(error),
            "status": status.HTTP_400_BAD_REQUEST,
            "amount": amount,
            "session_url": session.url,
            "session_id": session.id,
        }

    except stripe.error.CardError as error:
        # Handle card error (e.g., invalid card number, expired card)
        response = {
            "error": str(error),
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


def check_card_number_length(value):
    """
    Check if the provided card number has a length of 16 digits.
    Raises a validation error if the length is not 16 digits.
    """
    if len(value) != 16:
        raise serializers.ValidationError("Card number must be 16 digits.")
