from django.db import models


class PartCategory(models.Model):
    name = models.CharField(max_length=60)


class Part(models.Model):
    part_num = models.CharField(max_length=25, primary_key=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(PartCategory, on_delete=models.DO_NOTHING)
    thumbnail = models.CharField(max_length=255, blank=True)
    colors = models.ManyToManyField('Color', through='Element')


class Color(models.Model):
    name = models.CharField(max_length=20)
    rgb = models.CharField(max_length=6)
    is_trans = models.BooleanField()
    parts = models.ManyToManyField(Part, through='Element')


class Element(models.Model):
    part = models.ForeignKey(Part, on_delete=models.DO_NOTHING)
    color = models.ForeignKey(Color, on_delete=models.DO_NOTHING)
    image_url = models.CharField(max_length=200, blank=True)
    lego_element_id = models.CharField(max_length=10, blank=True)
