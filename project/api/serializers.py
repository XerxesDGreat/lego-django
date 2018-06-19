from django.contrib.auth.models import User
from project.api import models
from rest_framework import serializers


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
            return obj.thumnail

        for c in obj.colors.all():
            entity = models.Element.objects.get(part=obj.part_num, color=c.id)
            if entity.image_url:
                return entity.image_url

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
    class Meta:
        model = models.UserElement
        fields = ('user', 'element', 'quantity_on_display', 'quantity_in_storage', 'created', 'updated')


class UserPartSerializer(serializers.Serializer):
    part_num = serializers.CharField(source='element__part__part_num')
    part_name = serializers.CharField(source='element__part__name')
    category = serializers.IntegerField(source='element__part__category')
    storage = serializers.IntegerField()
    display = serializers.IntegerField()
    color_count = serializers.IntegerField()
