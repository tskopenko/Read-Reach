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
router.register("", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
