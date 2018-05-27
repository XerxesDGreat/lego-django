from django.db import models


class PartCategory(models.Model):
    name = models.CharField(max_length=60)


class Part(models.Model):
    part_num = models.CharField(max_length=25, primary_key=True)
    name = models.CharField(max_length=200)
    part_cat_id = models.ForeignKey(PartCategory, on_delete=models.DO_NOTHING)
    thumbnail = models.CharField(max_length=255, blank=True)
