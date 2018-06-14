from django.contrib.auth.models import User
from project.api import models
from rest_framework import viewsets, response, permissions
from project.api import serializers
import logging

logger = logging.getLogger(__name__)


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


class ElementViewSet(viewsets.ModelViewSet):
    queryset = models.Element.objects.all().order_by('part').order_by('color')
    serializer_class = serializers.ElementSerializer

    def get_queryset(self):
        part_id = self.request.query_params.get('part', None)
        if part_id is not None:
            return self.queryset.filter(part=part_id)
        return self.queryset


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, pk=None):
        if pk == 'me':
            logger.info(request.user)
            logger.info(request)
            return response.Response(serializers.UserSerializer(request.user, context={'request': request}).data)
        return super(UserViewSet, self).retrieve(request, pk)


class UserElementViewSet(viewsets.ModelViewSet):
    queryset = models.UserElement.objects.all().order_by('-created')
    serializer_class = serializers.UserElementSerializer
    permission_classes = (permissions.IsAuthenticated,)
