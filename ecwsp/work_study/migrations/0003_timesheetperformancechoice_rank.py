# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ecwsp.work_study.models


class Migration(migrations.Migration):

    dependencies = [
        ('work_study', '0002_auto_20140720_1735'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheetperformancechoice',
            name='rank',
            field=models.IntegerField(help_text=b'Must be unique. Convention is that higher numbers are better.', unique=True),
            preserve_default=True,
        ),
    ]
