# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ecwsp.work_study.models


class Migration(migrations.Migration):

    dependencies = [
        ('work_study', '0003_timesheetperformancechoice_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timesheetperformancechoice',
            name='rank',
            field=models.IntegerField(default=ecwsp.work_study.models.get_next_rank, help_text=b'Must be unique. Convention is that higher numbers are better.', unique=True),
        ),
    ]
