from django.contrib.auth.models import User
from rest_framework import viewsets
from project.api.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint which allows CRUD operations on Users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
