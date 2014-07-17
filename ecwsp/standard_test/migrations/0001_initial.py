# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('is_total', models.BooleanField(default=False, help_text=b'This is the actual total. Use this for tests that do not use simple addition to calculate final scores.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StandardCategoryGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grade', models.DecimalField(max_digits=6, decimal_places=2)),
                ('category', models.ForeignKey(to='standard_test.StandardCategory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StandardTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('calculate_total', models.BooleanField(default=False, help_text=b'Automatically calculate the total score by adding others together.')),
                ('cherry_pick_categories', models.BooleanField(default=False, help_text=b'Cherry pick results to generate total. Goes through each category and picks best scores, then calculates the total.')),
                ('cherry_pick_final', models.BooleanField(default=False, help_text=b'Cherry pick results to get total. Only use final scores.')),
                ('show_on_reports', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='standardcategory',
            name='test',
            field=models.ForeignKey(to='standard_test.StandardTest'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='StandardTestResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.date(2014, 7, 16), validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('show_on_reports', models.BooleanField(default=True, help_text=b"If true, show this test result on a report such as a transcript. Note entire test types can be marked as shown on report or not. This is useful if you have a test that is usually shown, but have a few instances where you don't want it to show.")),
                ('student', models.ForeignKey(to='sis.Student')),
                ('test', models.ForeignKey(to='standard_test.StandardTest')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='standardcategorygrade',
            name='result',
            field=models.ForeignKey(to='standard_test.StandardTestResult'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='standardtestresult',
            unique_together=set([(b'date', b'student', b'test')]),
        ),
    ]
