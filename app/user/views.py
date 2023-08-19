"""
Views for the user API.
"""
from rest_framework.generics import CreateAPIView
from .serializers import UserSerializer

class CreateUserAPIView(CreateAPIView):
    """Create a new user."""
    serializer_class = UserSerializer


