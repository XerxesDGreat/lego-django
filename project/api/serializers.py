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


class PartSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Part
        fields = ('url', 'part_num', 'name', 'part_cat_id', 'thumbnail')
