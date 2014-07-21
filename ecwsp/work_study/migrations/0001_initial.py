# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import re
import ecwsp.sis.helper_functions
import custom_field.custom_field
import ckeditor.fields
import django.db.models.deletion
from django.conf import settings
import ecwsp.work_study.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attendance', '0002_auto_20140716_1655'),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('absence_date', models.DateField(default=datetime.datetime.now, verbose_name=b'date', validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('tardy', models.CharField(default=b'P', max_length=1, verbose_name=b'Status', choices=[(b'P', b'Present'), (b'A', b'Absent/Half Day'), (b'T', b'Tardy'), (b'N', b'No Timesheet')])),
                ('tardy_time_in', models.TimeField(null=True, blank=True)),
                ('makeup_date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('paid', models.DecimalField(help_text=b'Dollar value student has paid school for a fee.', null=True, max_digits=5, decimal_places=2, blank=True)),
                ('billed', models.BooleanField(default=False, help_text=b'Has the student been billed for this day?')),
                ('half_day', models.BooleanField(default=False, help_text=b'Missed only half day.')),
                ('waive', models.BooleanField(default=False, help_text=b'Does not need to make up day at work.')),
                ('notes', models.CharField(max_length=255, blank=True)),
                ('sis_attendance', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='attendance.StudentAttendance', null=True)),
            ],
            options={
                'verbose_name_plural': b'Attendance',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttendanceFee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.IntegerField(help_text=b'Dollar value of attendance fee')),
            ],
            options={
                'verbose_name_plural': b'Attendances: Fees',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='attendance',
            name='fee',
            field=models.ForeignKey(blank=True, to='work_study.AttendanceFee', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='AttendanceReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': b'Attendances: Reason',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='attendance',
            name='reason',
            field=models.ForeignKey(blank=True, to='work_study.AttendanceReason', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ClientVisit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dol', models.BooleanField(default=False)),
                ('date', models.DateField(default=datetime.datetime.now, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('attendance_and_punctuality', models.CharField(blank=True, max_length=1, choices=[(b'4', b'Above and beyond'), (b'3', b'Represents high level of proficiency'), (b'2', b'On the way with some help'), (b'1', b'Needs immediate intervention')])),
                ('attitude_and_motivation', models.CharField(blank=True, max_length=1, choices=[(b'4', b'Above and beyond'), (b'3', b'Represents high level of proficiency'), (b'2', b'On the way with some help'), (b'1', b'Needs immediate intervention')])),
                ('productivity_and_time_management', models.CharField(blank=True, max_length=1, choices=[(b'4', b'Above and beyond'), (b'3', b'Represents high level of proficiency'), (b'2', b'On the way with some help'), (b'1', b'Needs immediate intervention')])),
                ('ability_to_learn_new_tasks', models.CharField(blank=True, max_length=1, choices=[(b'4', b'Above and beyond'), (b'3', b'Represents high level of proficiency'), (b'2', b'On the way with some help'), (b'1', b'Needs immediate intervention')])),
                ('professional_appearance', models.CharField(blank=True, max_length=1, choices=[(b'4', b'Above and beyond'), (b'3', b'Represents high level of proficiency'), (b'2', b'On the way with some help'), (b'1', b'Needs immediate intervention')])),
                ('interaction_with_coworkers', models.CharField(blank=True, max_length=1, choices=[(b'4', b'Above and beyond'), (b'3', b'Represents high level of proficiency'), (b'2', b'On the way with some help'), (b'1', b'Needs immediate intervention')])),
                ('initiative_and_self_direction', models.CharField(blank=True, max_length=1, choices=[(b'4', b'Above and beyond'), (b'3', b'Represents high level of proficiency'), (b'2', b'On the way with some help'), (b'1', b'Needs immediate intervention')])),
                ('accuracy_and_attention_to_detail', models.CharField(blank=True, max_length=1, choices=[(b'4', b'Above and beyond'), (b'3', b'Represents high level of proficiency'), (b'2', b'On the way with some help'), (b'1', b'Needs immediate intervention')])),
                ('organizational_skills', models.CharField(blank=True, max_length=1, choices=[(b'4', b'Above and beyond'), (b'3', b'Represents high level of proficiency'), (b'2', b'On the way with some help'), (b'1', b'Needs immediate intervention')])),
                ('observations', models.TextField(blank=True)),
                ('supervisor_comments', models.TextField(blank=True)),
                ('student_comments', models.TextField(blank=True)),
                ('job_description', models.TextField(blank=True)),
                ('work_environment', models.CharField(blank=True, max_length=1, choices=[(b'C', b'Safe / Compliant'), (b'N', b'Not Compliant')])),
                ('notify_mentors', models.BooleanField(default=False, help_text=b'E-mail this report to all those in the mentors group.')),
                ('notes', models.TextField(blank=True)),
                ('follow_up_of', models.ForeignKey(blank=True, to='work_study.ClientVisit', help_text=b'This report is a follow-up of selected report.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('alternative_contract_template', models.FileField(help_text=b'Optionally use this odt template instead of a global template for this particular company.', null=True, upload_to=b'contracts_alt', blank=True)),
            ],
            options={
                'ordering': (b'name',),
                'verbose_name_plural': b'Companies',
            },
            bases=(models.Model, custom_field.custom_field.CustomFieldModel),
        ),
        migrations.CreateModel(
            name='CompanyHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.datetime.now, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('fired', models.BooleanField(default=False)),
            ],
            options={
                'ordering': (b'-date',),
                'verbose_name_plural': b'Companies: History',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompContract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=255, blank=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('date', models.DateField(default=datetime.datetime.now, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('number_students', models.IntegerField(null=True, blank=True)),
                ('student_functional_responsibilities_other', models.TextField(blank=True)),
                ('student_desired_skills_other', models.TextField(blank=True)),
                ('student_leave', models.BooleanField(default=False)),
                ('student_leave_lunch', models.BooleanField(default=False, verbose_name=b'Student leaves for lunch.')),
                ('student_leave_errands', models.BooleanField(default=False, verbose_name=b'Student leaves for errands.')),
                ('student_leave_other', models.TextField(blank=True)),
                ('signed', models.BooleanField(default=False)),
                ('contract_file', models.FileField(upload_to=b'contracts', blank=True)),
                ('ip_address', models.IPAddressField(help_text=b'IP address when signed', null=True, blank=True)),
                ('company', models.ForeignKey(to='work_study.Company')),
                ('school_year', models.ForeignKey(blank=True, to='sis.SchoolYear', null=True)),
            ],
            options={
                'verbose_name': b'Company contract',
            },
            bases=(models.Model, custom_field.custom_field.CustomFieldModel),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.CharField(max_length=36, unique=True, null=True, blank=True)),
                ('fname', models.CharField(max_length=150, null=True, blank=True)),
                ('lname', models.CharField(max_length=150, null=True, blank=True)),
                ('title', models.CharField(max_length=150, null=True, blank=True)),
                ('phone', models.CharField(max_length=25, null=True, blank=True)),
                ('phone_cell', models.CharField(max_length=25, null=True, blank=True)),
                ('fax', models.CharField(max_length=25, null=True, blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
            ],
            options={
                'ordering': (b'lname',),
                'verbose_name': b'Contact supervisor',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='clientvisit',
            name='supervisor',
            field=models.ManyToManyField(to='work_study.Contact', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='CraContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.BooleanField(default=False, help_text=b'Receive daily e-mail listing all supervisor comments about student.')),
                ('email_all', models.BooleanField(default=False, help_text=b'Receive comments about all students.')),
                ('name', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': b'Contact CRA',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='clientvisit',
            name='cra',
            field=models.ForeignKey(blank=True, to='work_study.CraContact', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='MessageToSupervisor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', ckeditor.fields.RichTextField(help_text=b'This message will be shown to supervisors upon log in.')),
                ('start_date', models.DateField(default=datetime.date.today, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('end_date', models.DateField(default=datetime.date.today, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PaymentOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('details', models.TextField(blank=True)),
                ('cost_per_student', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='compcontract',
            name='payment',
            field=models.ForeignKey(default=9999, blank=True, to='work_study.PaymentOption', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Personality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(unique=True, max_length=4)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': (b'type',),
                'verbose_name_plural': b'Personality types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PickupLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.CharField(help_text=b'Cannot contain spaces', unique=True, max_length=20, validators=[django.core.validators.RegexValidator(regex=re.compile(b'^[A-z\\-_1234567890]+$'))])),
                ('long_name', models.CharField(max_length=255, blank=True)),
                ('directions', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': b'Companies: pickup',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PresetComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=255)),
            ],
            options={
                'ordering': (b'comment',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentDesiredSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='compcontract',
            name='student_desired_skills',
            field=models.ManyToManyField(to='work_study.StudentDesiredSkill', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='StudentFunctionalResponsibility',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': b'Student functional responsibilities',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='compcontract',
            name='student_functional_responsibilities',
            field=models.ManyToManyField(to='work_study.StudentFunctionalResponsibility', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='StudentInteraction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('type', models.CharField(max_length=1, choices=[(b'M', b'Mentoring'), (b'D', b'Discipline'), (b'P', b'Parent'), (b'C', b'Company'), (b'S', b'Supervisor'), (b'O', b'Other')])),
                ('comments', models.TextField(blank=True)),
                ('preset_comment', models.ManyToManyField(to='work_study.PresetComment', blank=True)),
                ('reported_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentWorker',
            fields=[
                ('student_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to='sis.Student')),
                ('day', models.CharField(blank=True, max_length=2, null=True, verbose_name=b'Working day', choices=[[b'M', b'Monday'], [b'T', b'Tuesday'], [b'W', b'Wednesday'], [b'TH', b'Thursday'], [b'F', b'Friday']])),
                ('transport_exception', models.CharField(blank=True, max_length=2, choices=[(b'AM', b'No AM'), (b'PM', b'No PM'), (b'NO', b'None')])),
                ('work_permit_no', ecwsp.sis.helper_functions.CharNullField(max_length=10, unique=True, null=True, blank=True)),
                ('school_pay_rate', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('student_pay_rate', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('adp_number', models.CharField(max_length=5, verbose_name=b'ADP Number', blank=True)),
                ('personality_type', models.ForeignKey(blank=True, to='work_study.Personality', null=True)),
                ('primary_contact', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='work_study.Contact', help_text=b'This is the primary supervisor to whom e-mails will be sent. If the desired contact is not showing, they may need to be added to the company. New contacts are not automatically assigned to a company unless the supervisor adds them.', null=True)),
            ],
            options={
                'ordering': (b'is_active', b'last_name', b'first_name'),
            },
            bases=('sis.student',),
        ),
        migrations.AddField(
            model_name='studentinteraction',
            name='student',
            field=models.ManyToManyField(to='work_study.StudentWorker', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyhistory',
            name='student',
            field=models.ForeignKey(to='work_study.StudentWorker'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clientvisit',
            name='student_worker',
            field=models.ForeignKey(blank=True, to='work_study.StudentWorker', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendance',
            name='student',
            field=models.ForeignKey(help_text=b'Student who was absent this day.', to='work_study.StudentWorker'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set([(b'student', b'absence_date')]),
        ),
        migrations.CreateModel(
            name='StudentWorkerRoute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='studentworker',
            name='pm_route',
            field=models.ForeignKey(blank=True, to='work_study.StudentWorkerRoute', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentworker',
            name='am_route',
            field=models.ForeignKey(blank=True, to='work_study.StudentWorkerRoute', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('survey', models.CharField(help_text=b'Title of survey, ex. MP2 2010', max_length=255)),
                ('question', models.CharField(max_length=255)),
                ('answer', models.CharField(max_length=510, blank=True)),
                ('date', models.DateField(default=datetime.datetime.now, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('student', models.ForeignKey(to='work_study.StudentWorker')),
            ],
            options={
                'ordering': (b'survey', b'student', b'question'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TimeSheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('for_pay', models.BooleanField(default=False, help_text=b'Student is working over break and will be paid separately for this work.')),
                ('make_up', models.BooleanField(default=False, help_text=b'Student is making up a missed day.', verbose_name=b'makeup')),
                ('creation_date', models.DateTimeField(auto_now_add=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('time_in', models.TimeField()),
                ('time_lunch', models.TimeField()),
                ('time_lunch_return', models.TimeField()),
                ('time_out', models.TimeField()),
                ('hours', models.DecimalField(null=True, max_digits=4, decimal_places=2, blank=True)),
                ('school_pay_rate', models.DecimalField(help_text=b'Per hour pay rate the school is receiving from a company.', null=True, max_digits=5, decimal_places=2, blank=True)),
                ('student_pay_rate', models.DecimalField(help_text=b'Per hour pay rate the student is actually receiving.', null=True, max_digits=5, decimal_places=2, blank=True)),
                ('school_net', models.DecimalField(null=True, max_digits=6, decimal_places=2, blank=True)),
                ('student_net', models.DecimalField(null=True, max_digits=6, decimal_places=2, blank=True)),
                ('approved', models.BooleanField(default=False, verbose_name=b'approve')),
                ('student_accomplishment', models.TextField(blank=True)),
                ('supervisor_comment', models.TextField(blank=True)),
                ('show_student_comments', models.BooleanField(default=True)),
                ('supervisor_key', models.CharField(max_length=20, blank=True)),
                ('cra_email_sent', models.BooleanField(default=False, help_text=b'This time sheet was sent to a CRA via nightly e-mail.', editable=False)),
                ('student', models.ForeignKey(to='work_study.StudentWorker')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WorkTeam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inactive', models.BooleanField(default=False, help_text=b"Will unset student's placements.")),
                ('team_name', models.CharField(unique=True, max_length=255)),
                ('paying', models.CharField(blank=True, max_length=1, choices=[(b'P', b'Paying'), (b'N', b'Non-Paying'), (b'F', b'Funded')])),
                ('funded_by', models.CharField(max_length=150, blank=True)),
                ('industry_type', models.CharField(max_length=100, blank=True)),
                ('travel_route', models.CharField(help_text=b'Train or van route', max_length=50, db_column=b'train_line', blank=True)),
                ('stop_location', models.CharField(max_length=150, blank=True)),
                ('address', models.CharField(max_length=150, blank=True)),
                ('city', models.CharField(max_length=150, blank=True)),
                ('state', models.CharField(max_length=2, blank=True)),
                ('zip', models.CharField(max_length=10, blank=True)),
                ('directions_to', models.TextField(blank=True)),
                ('directions_pickup', models.TextField(blank=True)),
                ('map', models.ImageField(upload_to=b'maps', blank=True)),
                ('use_google_maps', models.BooleanField(default=False)),
                ('company_description', models.TextField(blank=True)),
                ('job_description', models.TextField(blank=True)),
                ('time_earliest', models.TimeField(null=True, blank=True)),
                ('time_latest', models.TimeField(null=True, blank=True)),
                ('time_ideal', models.TimeField(null=True, blank=True)),
                ('am_transport_group', models.ForeignKey(db_column=b'dropoff_location_id', blank=True, to='work_study.PickupLocation', help_text=b'Group for morning drop-off, can be used for work study attendance.', null=True)),
                ('company', models.ForeignKey(blank=True, to='work_study.Company', null=True)),
                ('contacts', models.ManyToManyField(to='work_study.Contact', blank=True)),
                ('cras', models.ManyToManyField(to='work_study.CraContact', null=True, blank=True)),
                ('pm_transport_group', models.ForeignKey(db_column=b'pickup_location_id', blank=True, to='work_study.PickupLocation', help_text=b'Group for evening pick-up, can be used for work study attendance. If same as dropoff, you may omit this field.', null=True)),
            ],
            options={
                'ordering': (b'team_name',),
            },
            bases=(models.Model, custom_field.custom_field.CustomFieldModel),
        ),
        migrations.AddField(
            model_name='timesheet',
            name='company',
            field=models.ForeignKey(to='work_study.WorkTeam'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='survey',
            name='company',
            field=models.ForeignKey(blank=True, to='work_study.WorkTeam', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentworker',
            name='placement',
            field=models.ForeignKey(blank=True, to='work_study.WorkTeam', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentinteraction',
            name='companies',
            field=models.ManyToManyField(to='work_study.WorkTeam', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyhistory',
            name='placement',
            field=models.ForeignKey(to='work_study.WorkTeam'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='companyhistory',
            unique_together=set([(b'student', b'placement', b'date')]),
        ),
        migrations.AddField(
            model_name='clientvisit',
            name='company',
            field=models.ForeignKey(to='work_study.WorkTeam'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='WorkTeamUser',
            fields=[
            ],
            options={
                'ordering': (b'last_name', b'first_name'),
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.AddField(
            model_name='workteam',
            name='login',
            field=models.ManyToManyField(to='work_study.WorkTeamUser', blank=True),
            preserve_default=True,
        ),
    ]
