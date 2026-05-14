from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import SignupSerializer, UserSerializer


class SignupView(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignupSerializer


class CurrentUserView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

