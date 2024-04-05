from django.urls import path

from payment.views import (
    PaymentAPI,
    PaymentListAPIView,
    PaymentDetailAPIView,
)


app_name = "payment"

urlpatterns = [
    path("", PaymentListAPIView.as_view(), name="payment_list"),
    path("<int:pk>/success/", PaymentDetailAPIView.as_view(), name="payment_detail"),
    path("make_payment/", PaymentAPI.as_view(), name="make_payment"),
]
