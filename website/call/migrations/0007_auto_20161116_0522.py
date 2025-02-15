# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-16 05:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('call', '0006_auto_20161116_0519'),
    ]

    operations = [
        migrations.AddField(
            model_name='politician',
            name='name',
            field=models.CharField(default='Pat Toomey', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='politician',
            name='extra_phones',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='call.Phone'),
        ),
    ]
