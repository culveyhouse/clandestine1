# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-15 05:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homesnacksweb', '0014_auto_20160314_2309'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertycurrent',
            name='cooling_info',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='propertycurrent',
            name='heating_info',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
