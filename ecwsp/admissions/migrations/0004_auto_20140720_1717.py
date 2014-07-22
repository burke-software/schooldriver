# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators
import django.db.models.deletion
import ecwsp.admissions.models


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0003_auto_20140717_0952'),
        ('sis', '0003_auto_20140717_1002'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicant',
            name='school_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=ecwsp.admissions.models.get_school_year, blank=True, to='sis.SchoolYear', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicant',
            name='email',
            field=models.EmailField(max_length=75, blank=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='parent_email',
            field=models.EmailField(max_length=75, blank=True),
        ),
        migrations.AlterField(
            model_name='applicantstandardtestresult',
            name='date',
            field=models.DateField(default=datetime.date(2014, 7, 20), validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))]),
        ),
    ]
