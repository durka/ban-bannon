# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-16 05:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('call', '0005_auto_20161116_0407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='politician',
            name='extra_phones',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='call.Phone'),
        ),
    ]
