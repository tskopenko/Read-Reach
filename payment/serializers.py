import datetime
from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "money_to_pay",
            "session_url",
            "session_id",
        )


class PaymentListSerializer(PaymentSerializer):
    class Meta(PaymentSerializer.Meta):
        fields = ("id", "status", "type", "borrowing", "money_to_pay")


class PaymentDetailSerializer(PaymentSerializer):
    book = serializers.CharField(source="borrowing.book_id.title", read_only=True)
    return_date = serializers.CharField(
        source="borrowing.expected_return_date", read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "return_date",
            "book",
            "money_to_pay",
            "session_url",
            "session_id",
        )


def check_expiry_month(value):
    if not 1 <= int(value) <= 12:
        raise serializers.ValidationError("Invalid expiry month.")


def check_expiry_year(value):
    today = datetime.datetime.now()
    if not int(value) >= today.year:
        raise serializers.ValidationError("Invalid expiry year.")


def check_cvc(value):
    if not 3 <= len(value) <= 4:
        raise serializers.ValidationError("Invalid cvc number.")


def check_payment_method(value):
    payment_method = value.lower()
    if payment_method not in ["card"]:
        raise serializers.ValidationError("Invalid payment_method.")


class CardInformationSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=150, required=True)
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
