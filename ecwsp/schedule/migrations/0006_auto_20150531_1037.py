# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_auto_20150316_2148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursesection',
            name='cohorts',
            field=models.ManyToManyField(to='sis.Cohort', blank=True),
        ),
        migrations.AlterField(
            model_name='coursesection',
            name='enrollments',
            field=models.ManyToManyField(to='sis.Student', through='schedule.CourseEnrollment', blank=True),
        ),
    ]
