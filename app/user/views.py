"""
Views for the user API.
"""
from rest_framework.views import Response, APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authentication import TokenAuthentication


class CreateUserAPIView(CreateAPIView):
    """Create a new user."""
    permission_classes = [~IsAuthenticated]
    serializer_class = UserSerializer


class CreateTokenAPIView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class DiscardTokenAPIView(APIView):
    """Discard auth token if user is authenticated"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        self.request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManageUserAPIView(RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
