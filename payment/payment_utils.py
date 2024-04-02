from datetime import date

import stripe
from django.urls import reverse


stripe.api_key = "sk_test_51P0m5x08clH0Ss5WyssxsIFAWt4DpDr3ykkBh7VdOrVRcl7rv2cCqOZZGzwX4r26TmJVs3O8oUYmWISC3bVVXDQX00sAsF15K5"
FINE_MULTIPLIER = 2


def calculate_amount_borrowing(borrowing):
    """
    Calculate the borrowing amount based on the daily fee
    of the book and the duration of the borrowing period.
    """
    sum_days = borrowing.expected_return_date - borrowing.borrow_date
    amount = (sum_days.days + 1) * borrowing.book.daily_fee
    return amount


def calculate_amount_fine(borrowing):

    """Calculate the fine amount for a late book return based
    on the daily fee of the book and the duration of the delay."""

    sum_days = date.today() - borrowing.expected_return_date
    amount = (sum_days.days + 1) * borrowing.book.daily_fee * FINE_MULTIPLIER
    return amount


def create_checkout_session(borrowing, request):

    """
    Creates a Stripe Checkout session for initial borrowing payment.
    """

    success_url = reverse(
        "payments:payment-success", kwargs={"pk": borrowing.id}
    )
    cancel_url = reverse(
        "payments:payment-cancel", kwargs={"pk": borrowing.id}
    )

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": int(
                        calculate_amount_borrowing(borrowing) * 100
                    ),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(success_url),
        cancel_url=request.build_absolute_uri(cancel_url),
    )
    return session


def create_fine_session(borrowing, request):

    """
    Creates a Stripe Checkout session for fine borrowing payment.
    """

    success_url = reverse(
        "payments:payment-fine-success", kwargs={"pk": borrowing.id}
    )
    cancel_url = reverse(
        "payments:payment-cancel", kwargs={"pk": borrowing.id}
    )

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Fine for" + borrowing.book.title,
                    },
                    "unit_amount": int(calculate_amount_fine(borrowing) * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(success_url),
        cancel_url=request.build_absolute_uri(cancel_url),
    )
    return session
