# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import datetime
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0004_auto_20140720_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicantAdditionalInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.TextField(null=True, blank=True)),
                ('applicant', models.ForeignKey(related_name='additionals', to='admissions.Applicant')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplicantCustomField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_name', models.CharField(max_length=50, null=True, blank=True)),
                ('is_field_integrated_with_applicant', models.BooleanField(default=False)),
                ('field_type', models.CharField(blank=True, max_length=50, null=True, help_text=b'Choose the type of field', choices=[(b'input', b'Small Text Field'), (b'textarea', b'Large Text Field'), (b'multiple', b'Dropdown Choices'), (b'radio', b'Multiple Choices'), (b'checkbox', b'Checkboxes'), (b'emergency_contact', b'Emergency Contact')])),
                ('field_label', models.CharField(help_text=b'Give this field a recognizable name', max_length=255, null=True, blank=True)),
                ('field_choices', models.TextField(help_text=b'List the choices you want displayed, \nseperated by commas. This is only valid for Dropdown, \nMultiple, and Checkbox field types', null=True, blank=True)),
                ('helptext', models.CharField(max_length=500, null=True, blank=True)),
                ('required', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentApplicationTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('is_default', models.BooleanField(default=False)),
                ('json_template', jsonfield.fields.JSONField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='applicantadditionalinformation',
            name='custom_field',
            field=models.ForeignKey(to='admissions.ApplicantCustomField', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicant',
            name='bday',
            field=models.DateField(null=True, verbose_name=b'Birth Date', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicant',
            name='elem_grad_yr',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicant',
            name='follow_up_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicant',
            name='hs_grad_yr',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicant',
            name='siblings',
            field=models.ManyToManyField(related_name='+', to='sis.Student', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicant',
            name='sis_student',
            field=models.OneToOneField(related_name='appl_student', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='sis.Student'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicantstandardtestresult',
            name='date',
            field=models.DateField(default=datetime.date(2014, 12, 31), validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='applicationdecisionoption',
            name='level',
            field=models.ManyToManyField(help_text=b'This decision can apply for these levels.', to='admissions.AdmissionLevel', null=True, blank=True),
            preserve_default=True,
        ),
    ]
