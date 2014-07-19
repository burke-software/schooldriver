# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models
import datetime
import ecwsp.volunteer_track.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hours',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('hours', models.FloatField()),
                ('time_stamp', models.DateTimeField(auto_now_add=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
            ],
            options={
                'verbose_name': b'Hours',
                'verbose_name_plural': b'Hours',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site_name', models.CharField(unique=True, max_length=255)),
                ('site_address', models.CharField(max_length=511)),
                ('site_city', models.CharField(max_length=768)),
                ('site_state', models.CharField(max_length=30)),
                ('site_zip', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteSupervisor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('phone', localflavor.us.models.PhoneNumberField(max_length=20, blank=True)),
                ('email', models.EmailField(max_length=200, blank=True)),
                ('site', models.ForeignKey(blank=True, to='volunteer_track.Site', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attended_reflection', models.BooleanField(default=False, verbose_name=b'Attended')),
                ('hours_required', models.IntegerField(default=ecwsp.volunteer_track.models.get_hours_default, null=True, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('last_updated', models.DateTimeField(default=datetime.datetime.now)),
                ('email_queue', models.CharField(default=b'', help_text=b'Used to store nightly notification emails.', max_length=1000, editable=False, blank=True)),
                ('student', models.OneToOneField(to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VolunteerSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inactive', models.BooleanField(default=False)),
                ('site_approval', models.CharField(blank=True, max_length=16, choices=[(b'Accepted', b'Accepted'), (b'Rejected', b'Rejected'), (b'Submitted', b'Submitted')])),
                ('contract', models.BooleanField(default=False)),
                ('job_description', models.TextField(blank=True)),
                ('hours_confirmed', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
                ('secret_key', models.CharField(max_length=20, editable=False, blank=True)),
                ('site', models.ForeignKey(to='volunteer_track.Site')),
                ('supervisor', models.ForeignKey(blank=True, to='volunteer_track.SiteSupervisor', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='sites',
            field=models.ManyToManyField(to='volunteer_track.Site', null=True, through='volunteer_track.VolunteerSite', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hours',
            name='volunteer_site',
            field=models.ForeignKey(to='volunteer_track.VolunteerSite'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='hours',
            unique_together=set([(b'volunteer_site', b'date')]),
        ),
        migrations.AddField(
            model_name='volunteersite',
            name='volunteer',
            field=models.ForeignKey(to='volunteer_track.Volunteer'),
            preserve_default=True,
        ),
    ]
