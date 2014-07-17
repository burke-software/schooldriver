# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '__latest__'),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerCourseSectionCohort',
            fields=[
                ('cohort_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to='sis.Cohort')),
                ('course_section', models.ForeignKey(to='schedule.CourseSection')),
            ],
            options={
            },
            bases=('sis.cohort',),
        ),
    ]
