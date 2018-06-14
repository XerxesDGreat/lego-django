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
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserElement
        fields = ('user', 'element', 'quantity_on_display', 'quantity_in_storage', 'created', 'updated')
