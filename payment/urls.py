from django.urls import path, include
from rest_framework import routers

from payment.views import (
    PaymentViewSet,
    PaymentSuccessView,
    PaymentCancelView,
    PaymentFineSuccessView,
)


app_name = "payment"

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:pk>/success_payment/",
        PaymentSuccessView.as_view(),
        name="success_payment"
    ),
    path(
        "<int:pk>/cancel_payment/",
        PaymentCancelView.as_view(),
        name="cancel_payment"
    ),
    path(
        "<int:pk>/success_fine_payment/",
        PaymentFineSuccessView.as_view(),
        name="success_fine_payment",
    ),
]
