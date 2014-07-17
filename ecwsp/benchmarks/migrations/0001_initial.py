# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Benchmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=10, null=True, blank=True)),
                ('name', models.CharField(max_length=700)),
            ],
            options={
                'ordering': (b'number', b'name'),
            },
            bases=(models.Model,),
        ),
    ]
