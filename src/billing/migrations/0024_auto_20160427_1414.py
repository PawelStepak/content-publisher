# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-27 14:14
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0023_auto_20160425_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='date_end',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 27, 14, 14, 19, 761669, tzinfo=utc), verbose_name=b'End Date'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='date_start',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 27, 14, 14, 19, 761609, tzinfo=utc), verbose_name=b'Start Date'),
        ),
    ]
