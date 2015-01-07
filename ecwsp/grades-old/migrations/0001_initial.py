# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators
import ecwsp.grades.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('grade', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('override_final', models.BooleanField(default=False, help_text=b'Override final grade for marking period instead of calculating it.')),
                ('comment', models.CharField(blank=True, max_length=500, validators=[ecwsp.grades.models.grade_comment_length_validator])),
                ('letter_grade', models.CharField(blank=True, max_length=2, null=True, help_text=b'Will override grade.', choices=[(b'I', b'Incomplete'), (b'P', b'Pass'), (b'F', b'Fail'), (b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'HP', b'High Pass'), (b'LP', b'Low Pass'), (b'M', b'Missing')])),
            ],
            options={
                'permissions': ((b'change_own_grade', b'Change grades for own class'), (b'change_own_final_grade', b'Change final YTD grades for own class')),
            },
            bases=(models.Model,),
        ),
    ]
