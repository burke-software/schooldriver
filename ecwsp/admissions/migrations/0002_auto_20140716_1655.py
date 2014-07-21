# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators
import django.db.models.deletion
from django.conf import settings
import ecwsp.admissions.models
import ecwsp.sis.models


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('standard_test', '0001_initial'),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicant',
            name='application_decision_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='sis.Faculty', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicant',
            name='checklist',
            field=models.ManyToManyField(to='admissions.AdmissionCheck', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicant',
            name='family_preferred_language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=ecwsp.sis.models.get_default_language, blank=True, to='sis.LanguageChoice', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicant',
            name='level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.AdmissionLevel', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicant',
            name='parent_guardians',
            field=models.ManyToManyField(to='sis.EmergencyContact', null=True, verbose_name=b'Student contact', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicant',
            name='siblings',
            field=models.ManyToManyField(to='sis.Student', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicant',
            name='sis_student',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='sis.Student'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicant',
            name='year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=ecwsp.admissions.models.get_year, blank=True, to='sis.GradeLevel', help_text=b'Applying for this grade level', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ApplicantFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('applicant_file', models.FileField(upload_to=b'applicant_files')),
                ('applicant', models.ForeignKey(to='admissions.Applicant')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplicantStandardCategoryGrade',
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
            name='ApplicantStandardTestResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.date(2014, 7, 16), validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('show_on_reports', models.BooleanField(default=True, help_text=b"If true, show this test result on a report such as a transcript. Note entire test types can be marked as shown on report or not. This is useful if you have a test that is usually shown, but have a few instances where you don't want it to show.")),
                ('applicant', models.ForeignKey(to='admissions.Applicant')),
                ('test', models.ForeignKey(to='standard_test.StandardTest')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicantstandardcategorygrade',
            name='result',
            field=models.ForeignKey(to='admissions.ApplicantStandardTestResult'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='applicantstandardtestresult',
            unique_together=set([(b'date', b'applicant', b'test')]),
        ),
        migrations.CreateModel(
            name='ApplicationDecisionOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('level', models.ManyToManyField(to='admissions.AdmissionLevel', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='application_decision',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.ApplicationDecisionOption', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='BoroughOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'ordering': [b'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='borough',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.BoroughOption', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ContactLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('note', models.TextField()),
                ('applicant', models.ForeignKey(to='admissions.Applicant')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CountryOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
            ],
            options={
                'ordering': [b'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='country_of_birth',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=ecwsp.admissions.models.get_default_country, blank=True, to='admissions.CountryOption', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='EthnicityChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': [b'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='ethnicity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.EthnicityChoice', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='FeederSchool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'ordering': [b'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='present_school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.FeederSchool', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='FirstContactOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'ordering': [b'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='first_contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.FirstContactOption', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='HeardAboutUsOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'ordering': [b'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='heard_about_us',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.HeardAboutUsOption', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ImmigrationOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
            ],
            options={
                'ordering': [b'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='immigration_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.ImmigrationOption', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='OpenHouse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
            ],
            options={
                'ordering': (b'-date',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='open_house_attended',
            field=models.ManyToManyField(to='admissions.OpenHouse', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='PlaceOfWorship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='place_of_worship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.PlaceOfWorship', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ReligionChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': [b'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='religion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.ReligionChoice', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='SchoolType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='feederschool',
            name='school_type',
            field=models.ForeignKey(blank=True, to='admissions.SchoolType', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='WithdrawnChoices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
            ],
            options={
                'ordering': [b'name'],
                'verbose_name_plural': b'Withdrawn choices',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicant',
            name='withdrawn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='admissions.WithdrawnChoices', null=True),
            preserve_default=True,
        ),
    ]
