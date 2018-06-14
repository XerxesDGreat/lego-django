from django.db import models
from django.contrib.auth.models import User


class PartCategory(models.Model):
    name = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Part(models.Model):
    part_num = models.CharField(max_length=25, primary_key=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(PartCategory, on_delete=models.DO_NOTHING)
    thumbnail = models.CharField(max_length=255, blank=True)
    colors = models.ManyToManyField('Color', through='Element')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Color(models.Model):
    name = models.CharField(max_length=20)
    rgb = models.CharField(max_length=6)
    is_trans = models.BooleanField()
    parts = models.ManyToManyField(Part, through='Element')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Element(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    image_url = models.CharField(max_length=200, blank=True)
    lego_element_id = models.CharField(max_length=10, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class UserElement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    quantity_on_display = models.IntegerField(default=0)
    quantity_in_storage = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
