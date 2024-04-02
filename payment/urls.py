from django.urls import path

from payment.views import (
    PaymentListView,
    PaymentDetailView,
    PaymentSuccessView,
    PaymentCancelView,
    CreatePaymentAPI,
)


app_name = "payment"


urlpatterns = [
    path("", PaymentListView.as_view(), name="payment_list"),
    path("payment/<int:pk>/", PaymentDetailView.as_view(), name='payment_detail'),
    path("make_payment/", CreatePaymentAPI.as_view(), name="make_payment"),
    path(
        "cancel_payment/",
        PaymentCancelView.as_view(),
        name="cancel_payment"
    ),
    path(
        "success_payment/",
        PaymentSuccessView.as_view(),
        name="success_payment",
    ),
]
