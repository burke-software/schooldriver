# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('standard_test', '0006_auto_20150204_0811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardtestresult',
            name='date',
            field=models.DateField(default=datetime.date(2015, 3, 16), validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))]),
            preserve_default=True,
        ),
    ]
