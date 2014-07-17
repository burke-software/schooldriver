# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import ecwsp.administration.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ua', models.CharField(help_text=b'User agent. We can use this to determine operating system and browser in use.', max_length=2000)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('ip', models.IPAddressField()),
                ('usage', models.CharField(max_length=255)),
                ('login', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('value', models.TextField(blank=True)),
                ('file', models.FileField(help_text=b'Some configuration options are for file uploads', null=True, upload_to=b'configuration', blank=True)),
                ('help_text', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('file', models.FileField(upload_to=b'templates', validators=[ecwsp.administration.models.validate_file_extension])),
                ('general_student', models.BooleanField(default=False, help_text=b'Can be used on student reports')),
                ('report_card', models.BooleanField(default=False, help_text=b'Can be used on grade reports, gathers data for one year')),
                ('benchmark_report_card', models.BooleanField(default=False, help_text=b'A highly detailed, single-year report card for benchmark-based grading')),
                ('transcript', models.BooleanField(default=False, help_text=b'Can be used on grade reports, gathers data for all years')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
