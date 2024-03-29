# Generated by Django 2.0.5 on 2018-06-10 05:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.CharField(max_length=200)),
                ('lego_element_id', models.IntegerField()),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='api.Color')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='api.Part')),
            ],
        ),
        migrations.AddField(
            model_name='color',
            name='parts',
            field=models.ManyToManyField(through='api.Element', to='api.Part'),
        ),
        migrations.AddField(
            model_name='part',
            name='colors',
            field=models.ManyToManyField(through='api.Element', to='api.Color'),
        ),
    ]
