from django.contrib.auth.models import User
from project.api import models
from rest_framework import viewsets
from project.api import serializers


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class PartCategoryViewSet(viewsets.ModelViewSet):
    queryset = models.PartCategory.objects.all()
    serializer_class = serializers.PartCategorySerializer


class PartViewSet(viewsets.ModelViewSet):
    queryset = models.Part.objects.all()
    serializer_class = serializers.PartSerializer
