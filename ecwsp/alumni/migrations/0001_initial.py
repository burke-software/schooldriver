# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alumni',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('graduated', models.BooleanField(default=False)),
                ('graduation_date', models.DateField(blank=True, help_text=b'Expected or actual graduation date', null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('college_override', models.BooleanField(default=False, help_text=b'If checked, college enrollment data will not set college and graduated automatically.')),
                ('program_years', models.CharField(blank=True, max_length=1, null=True, choices=[(b'4', b'4-year or higher institution'), (b'2', b'2-year institution'), (b'L', b'less than 2-year institution')])),
                ('semesters', models.CharField(help_text=b'Number of semesters or trimesters.', max_length=b'5', blank=True)),
                ('on_track', models.BooleanField(default=False, help_text=b'On track to graduate')),
            ],
            options={
                'verbose_name_plural': b'Alumni',
            },
            bases=(models.Model,),
        ),
    ]
