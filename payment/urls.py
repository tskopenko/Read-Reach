from django.urls import path, include
from rest_framework import routers

from payment.views import (
    PaymentViewSet,
    PaymentSuccessView,
    PaymentCancelView,
    PaymentFineSuccessView,
)


app_name = "payments"

router = routers.DefaultRouter()
router.register("", PaymentViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:pk>/success_payment/",
        PaymentSuccessView.as_view(),
        name="payment-success",
    ),
    path(
        "<int:pk>/success_fine_payment/",
        PaymentFineSuccessView.as_view(),
        name="payment-fine-success",
    ),
    path(
        "<int:pk>/cancel_payment/",
        PaymentCancelView.as_view(),
        name="payment-cancel",
    ),
]
