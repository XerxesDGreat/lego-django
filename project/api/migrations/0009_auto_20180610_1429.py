# Generated by Django 2.0.5 on 2018-06-10 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20180610_0531'),
    ]

    operations = [
        migrations.RenameField(
            model_name='part',
            old_name='part_cat_id',
            new_name='category',
        ),
    ]
