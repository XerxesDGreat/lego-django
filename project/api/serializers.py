from django.contrib.auth.models import User
from project.api import models
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class PartCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.PartCategory
        fields = ('id', 'name')


class PartSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Part
        fields = ('part_num', 'name', 'category', 'thumbnail_url', 'colors')

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
        fields = ('id', 'name', 'is_trans', 'rgb')


class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Element
        fields = ('part', 'color', 'image_url', 'lego_element_id')
