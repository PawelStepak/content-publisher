# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-17 09:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0044_auto_20160511_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageview',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]