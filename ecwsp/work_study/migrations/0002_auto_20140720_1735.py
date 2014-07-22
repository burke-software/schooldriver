# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ecwsp.work_study.models


class Migration(migrations.Migration):

    dependencies = [
        ('work_study', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSheetPerformanceChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'ordering': (b'rank',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='performance',
            field=models.ForeignKey(blank=True, to='work_study.TimeSheetPerformanceChoice', null=True),
            preserve_default=True,
        ),
    ]
