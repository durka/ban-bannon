# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-19 06:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('call', '0014_politician_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='politician',
            name='title',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
