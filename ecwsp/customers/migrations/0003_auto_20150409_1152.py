# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_auto_20150409_1023'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignUp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('domain_url', models.CharField(max_length=100)),
                ('client_name', models.CharField(max_length=100)),
                ('client_email', models.EmailField(max_length=75)),
                ('client_number', models.CharField(max_length=10, blank=True)),
                ('status', models.CharField(default=b'S', max_length=1, choices=[(b'S', b'Started'), (b'D', b'Done'), (b'F', b'Failed')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='client',
            name='client_email',
        ),
        migrations.RemoveField(
            model_name='client',
            name='client_name',
        ),
        migrations.RemoveField(
            model_name='client',
            name='client_number',
        ),
    ]
