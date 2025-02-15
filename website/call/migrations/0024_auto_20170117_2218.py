# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-17 22:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('call', '0023_auto_20170112_2047'),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(choices=[('N', 'Has not said'), ('S', 'Supports'), ('D', 'Denounces')], default='N', max_length=1)),
                ('script', models.TextField(blank=True, default=None)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='call.Campaign')),
            ],
        ),
        migrations.RemoveField(
            model_name='politician',
            name='position',
        ),
        migrations.RemoveField(
            model_name='politician',
            name='script',
        ),
        migrations.AddField(
            model_name='position',
            name='politician',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='call.Politician'),
        ),
    ]
