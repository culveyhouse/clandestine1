# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-03 15:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homesnacksweb', '0011_auto_20160203_1024'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='propertycurrent',
            unique_together=set([('mls', 'mls_property_id')]),
        ),
        migrations.AlterIndexTogether(
            name='propertycurrent',
            index_together=set([]),
        ),
    ]
