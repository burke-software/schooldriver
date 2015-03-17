# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_auto_20150102_1238'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='courseenrollment',
            name='cached_grade',
        ),
        migrations.RemoveField(
            model_name='courseenrollment',
            name='cached_numeric_grade',
        ),
        migrations.RemoveField(
            model_name='courseenrollment',
            name='grade_recalculation_needed',
        ),
        migrations.RemoveField(
            model_name='courseenrollment',
            name='numeric_grade_recalculation_needed',
        ),
    ]
