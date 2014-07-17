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
            name='DisciplineAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('major_offense', models.BooleanField(default=False, help_text=b'This can be filtered by Grade Analytics and other reports.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DisciplineActionInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(default=1)),
                ('action', models.ForeignKey(to='discipline.DisciplineAction')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Infraction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(help_text=b'If comment is "Case note" these infractions will not be counted as a discipline issue in reports', max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentDiscipline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.datetime.today, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('comments', models.TextField(blank=True)),
                ('private_note', models.TextField(blank=True)),
            ],
            options={
                'ordering': (b'-date',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='disciplineactioninstance',
            name='student_discipline',
            field=models.ForeignKey(to='discipline.StudentDiscipline'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentdiscipline',
            name='action',
            field=models.ManyToManyField(to='discipline.DisciplineAction', through='discipline.DisciplineActionInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentdiscipline',
            name='infraction',
            field=models.ForeignKey(blank=True, to='discipline.Infraction', null=True),
            preserve_default=True,
        ),
    ]
