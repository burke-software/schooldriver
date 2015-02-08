# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0005_auto_20150118_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicantstandardtestresult',
            name='date',
            field=models.DateField(default=datetime.date(2015, 2, 4), validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))]),
            preserve_default=True,
        ),
    ]
