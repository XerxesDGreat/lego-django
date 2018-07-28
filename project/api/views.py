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


class CategoryFilterMixin(object):
    def filter_by_category_id(self, queryset):
        category = None
        category_id = self.request.query_params.get('category_id', None)
        if category_id is not None:
            try:
                category = models.PartCategory.objects.get(pk=category_id)
            except models.PartCategory.DoesNotExist:
                category = None
        print('category: %s' % category)
        if category is not None:
            queryset = queryset.filter(category=category)

        return queryset


class PartViewSet(viewsets.ModelViewSet, CategoryFilterMixin):
    queryset = models.Part.objects.all()
    serializer_class = serializers.PartSerializer

    def get_queryset(self):
        """
        Override default functionality to allow filtering of parts
        :return:
        """
        queryset = models.Part.objects.filter(meta=0).order_by('part_num')
        queryset = self.filter_by_category_id(queryset)

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
            return response.Response(serializers.UserSerializer(request.user, context={'request': request}).data)
        return super(UserViewSet, self).retrieve(request, pk)


class UserElementViewSet(viewsets.ModelViewSet):
    queryset = models.UserElement.objects.all().order_by('-created')
    serializer_class = serializers.UserElementSerializer
    permission_classes = (permissions.IsAuthenticated,)


class UserPartsViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin, CategoryFilterMixin):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserPartSerializer

    def get_queryset(self):
        queryset = models.Part.objects.all() \
            .distinct() \
            .filter(element__userelement__user=self.request.user) \
            .order_by('part_num')
        queryset = self.filter_by_category_id(queryset)

        return queryset


class SetViewSet(viewsets.ModelViewSet):
    queryset = models.Set.objects.all().order_by('set_num')
    serializer_class = serializers.SetSerializer


class SetThemeViewSet(viewsets.ModelViewSet):
    queryset = models.SetTheme.objects.all()
    serializer_class = serializers.SetThemeSerializer
