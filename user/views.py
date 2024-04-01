from django.conf import settings
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from user.serializers import UserSerializer


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
