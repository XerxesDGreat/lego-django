# Generated by Django 2.0.5 on 2018-06-10 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20180610_0528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='element',
            name='lego_element_id',
            field=models.IntegerField(blank=True),
        ),
    ]
