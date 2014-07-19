# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0002_auto_20140716_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicantstandardtestresult',
            name='date',
            field=models.DateField(default=datetime.date(2014, 7, 17), validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))]),
        ),
    ]
