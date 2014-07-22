# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0001_initial'),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='benchmark',
            name='year',
            field=models.ForeignKey(blank=True, to='sis.GradeLevel', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MeasurementTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('department', models.ForeignKey(blank=True, to='benchmarks.Department', null=True)),
            ],
            options={
                'ordering': (b'department', b'name'),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='benchmark',
            name='measurement_topics',
            field=models.ManyToManyField(to='benchmarks.MeasurementTopic'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='measurementtopic',
            unique_together=set([(b'name', b'department')]),
        ),
    ]
