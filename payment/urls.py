from django.urls import path

from payment.views import (
    PaymentAPI,
    PaymentListAPIView,
    PaymentDetailAPIView,
)


app_name = "payment"

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payment_list"),
    path("payments/<int:pk>/", PaymentDetailAPIView.as_view(), name="payment_detail"),
    path("payments/make_payment/", PaymentAPI.as_view(), name="make_payment"),
]
