# Generated by Django 2.0.5 on 2018-05-27 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='part',
            name='id',
        ),
        migrations.AlterField(
            model_name='part',
            name='part_num',
            field=models.CharField(max_length=25, primary_key=True, serialize=False),
        ),
    ]