# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-19 07:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('call', '0018_auto_20161119_0708'),
    ]

    operations = [
        migrations.RenameField(
            model_name='politician',
            old_name='title',
            new_name='leadership_role',
        ),
    ]
