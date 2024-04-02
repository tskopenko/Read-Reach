from django.urls import path, include
from rest_framework import routers

from payment.views import (
    PaymentViewSet,
    PaymentSuccessView,
    PaymentCancelView,
    PaymentAPI,
)


app_name = "payment"

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("make_payment/", PaymentAPI.as_view(), name="make_payment"),
    path(
        "cancel_payment/",
        PaymentCancelView.as_view(),
        name="cancel_payment"
    ),
    path(
        "success/",
        PaymentSuccessView.as_view(),
        name="success_payment",
    ),
]
