# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0021_auto_20160422_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='date_end',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 22, 20, 20, 22, 948783, tzinfo=utc), verbose_name=b'End Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='membership',
            name='date_start',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 22, 20, 20, 22, 948714, tzinfo=utc), verbose_name=b'Start Date'),
            preserve_default=True,
        ),
    ]
