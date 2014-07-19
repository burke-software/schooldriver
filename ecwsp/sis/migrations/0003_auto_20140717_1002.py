# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0002_percoursesectioncohort'),
    ]

    operations = [
        migrations.CreateModel(
            name='GradeScale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GradeScaleRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_grade', models.DecimalField(max_digits=5, decimal_places=2)),
                ('max_grade', models.DecimalField(max_digits=5, decimal_places=2)),
                ('letter_grade', models.CharField(max_length=50, blank=True)),
                ('numeric_scale', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('grade_scale', models.ForeignKey(to='sis.GradeScale')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='gradescalerule',
            unique_together=set([(b'min_grade', b'max_grade', b'grade_scale')]),
        ),
        migrations.AddField(
            model_name='schoolyear',
            name='grade_scale',
            field=models.ForeignKey(blank=True, to='sis.GradeScale', help_text=b'Alternative grade scale such as letter grades or a 4.0 scale', null=True),
            preserve_default=True,
        ),
    ]
