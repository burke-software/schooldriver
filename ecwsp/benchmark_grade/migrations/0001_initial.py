# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aggregate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('manual_mark', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('cached_value', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('cached_substitution', models.CharField(max_length=16, null=True, blank=True)),
                ('points_possible', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
