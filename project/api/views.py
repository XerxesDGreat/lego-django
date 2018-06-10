from django.contrib.auth.models import User
from project.api import models
from rest_framework import viewsets
from project.api import serializers


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class PartCategoryViewSet(viewsets.ModelViewSet):
    queryset = models.PartCategory.objects.all().order_by('name')
    serializer_class = serializers.PartCategorySerializer


class ColorViewSet(viewsets.ModelViewSet):
    queryset = models.Color.objects.all().order_by('id')
    serializer_class = serializers.ColorSerializer


class PartViewSet(viewsets.ModelViewSet):
    queryset = models.Part.objects.all()
    serializer_class = serializers.PartSerializer

    def get_queryset(self):
        """
        Override default functionality to allow filtering of parts
        :return:
        """
        queryset = models.Part.objects.all().order_by('part_num')
        category_id = self.request.query_params.get('category_id', None)
        if category_id is not None:
            queryset = queryset.filter(category=category_id)
        return queryset
