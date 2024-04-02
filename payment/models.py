from enum import Enum

from django.db import models

from borrowing.models import Borrowing


class PaymentStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class PaymentType(Enum):
    PAYMENT = "PAYMENT"
    FINE = "FINE"


class Payment(models.Model):
    """
    Represents a payment made in the system.
    """

    status = models.CharField(
        max_length=10, choices=[(status.value, status.name) for status in PaymentStatus]
    )
    type = models.CharField(
        max_length=10, choices=[(type_.value, type_.name) for type_ in PaymentType]
    )
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=100)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self
