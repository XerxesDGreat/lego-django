from django.contrib.auth.models import User
from project.api import models
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)


class PartCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.PartCategory
        fields = ('id', 'name')


class PartSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Part
        fields = ('part_num', 'name', 'category', 'thumbnail_url', 'colors', 'created', 'updated')

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return obj.thumbnail

        return ''


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Color
        fields = ('id', 'name', 'is_trans', 'rgb', 'created', 'updated')


class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Element
        fields = ('id', 'part', 'color', 'image_url', 'lego_element_id', 'created', 'updated')


class UserSerializer(serializers.ModelSerializer):
    parts = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        self.add_details = self.context['request'].query_params.get('details') == '1'
        if not self.add_details:
            self.fields.pop('parts')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'parts')

    def get_parts(self, obj):
        if not self.add_details:
            return None
        elements = models.UserElement.objects.filter(user=obj)
        elements_count = {
            'storage': 0,
            'display': 0
        }
        for element in elements:
            elements_count['storage'] += element.quantity_in_storage
            elements_count['display'] += element.quantity_on_display
        return elements_count


class UserElementSerializer(serializers.ModelSerializer):
    element = ElementSerializer()

    class Meta:
        model = models.UserElement
        fields = '__all__'


class UserPartSerializer(PartSerializer):
    owned_elements = serializers.SerializerMethodField()

    class Meta:
        model = models.Part
        fields = ('part_num', 'name', 'category', 'thumbnail_url', 'colors', 'created', 'updated', 'owned_elements')

    def get_owned_elements(self, obj):
        elements = models.UserElement.objects \
            .filter(element__part__part_num=obj.part_num,
                    user=self.context['request'].user) \
            .select_related('element')
        return UserElementSerializer(many=True).to_representation(elements)


class SetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Set
        fields = '__all__'


class SetThemeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = models.SetTheme
        fields = '__all__'

    def get_full_name(self, obj):
        return obj.get_name()
