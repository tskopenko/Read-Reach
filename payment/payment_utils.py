import os
from typing import Union

import stripe

from rest_framework import status
from rest_framework.response import Response

from borrowing.models import Borrowing
from payment.models import PaymentType, Payment


stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
LOCAL_DOMAIN = "http://127.0.0.1:8000/"


def calculate_full_price(pk: int, type_: str):
    """
    Calculates the full price for a borrowing based on the type of payment.

    Args:
        pk (int): The ID of the borrowing.
        type_ (str): The type of payment (either 'PAYMENT' or 'FINE').

    Returns:
        int: The calculated full price in cents.
    """
    try:
        borrowing = Borrowing.objects.get(id=pk)
        price = borrowing.book.daily_fee
        expected_return_date = borrowing.expected_return_date
        if type_ == PaymentType.PAYMENT.value:
            actual_date = borrowing.borrow_date
            delta = expected_return_date - actual_date
            number_of_days = delta.days
            return number_of_days * price * 100
        elif type_ == PaymentType.FINE.value:
            actual_date = borrowing.actual_return_date
            delta = actual_date - expected_return_date
            number_of_days = delta.days
            return number_of_days * price * 2 * 100
        else:
            raise ValueError("Invalid payment type")
    except Borrowing.DoesNotExist:
        raise ValueError("Borrowing not found")


def create_checkout_session(pk: int, type_: str) -> Union[Response, None]:
    """
    Creates a checkout session for the borrowing payment.

    Args:
        pk (int): The ID of the borrowing.
        type_ (str): The type of payment (either 'PAYMENT' or 'FINE').

    Returns:
        Union[JsonResponse, None]: Returns JsonResponse with error message in case of failure, None otherwise.
    """
    try:
        borrowing = Borrowing.objects.get(id=pk)
        price = calculate_full_price(pk, type_)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount_decimal": int(price),
                        "product_data": {
                            "name": borrowing.book.title,
                            "description": f"Author: {borrowing.book.author}",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{LOCAL_DOMAIN}api/borrowings/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{LOCAL_DOMAIN}api/borrowings/canceled/",
        )
        Payment.objects.create(
            borrowing=borrowing,
            session_url=checkout_session.url,
            session_id=checkout_session.stripe_id,
            type=type_,
            money_to_pay=checkout_session.amount_total,
        )
        return Response("Checkout session created successfully", status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)