from rest_framework import serializers

from borrowing.models import Borrowing
from .models import Payment
from payment.payment_utils import (
    check_expiry_month,
    check_expiry_year,
    check_cvc,
    check_card_number_length,
)


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentListSerializer(PaymentSerializer):

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "money_to_pay"
        )


class PaymentDetailSerializer(PaymentSerializer):

    book = serializers.CharField(
        source="borrowing.book_id.title", read_only=True
    )
    return_date = serializers.CharField(
        source="borrowing.expected_return_date", read_only=True
    )
    user = serializers.CharField(
        source="borrowing.user.email", read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "status",
            "return_date",
            "book",
            "money_to_pay",
            "session_url",
            "session_id",
        )


class CardInformationSerializer(serializers.Serializer):
    card_number = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_card_number_length]
    )
    expiry_month = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_expiry_month],
    )
    expiry_year = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_expiry_year],
    )
    cvc = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_cvc],
    )
    borrowing = serializers.PrimaryKeyRelatedField(queryset=Borrowing.objects.all())
