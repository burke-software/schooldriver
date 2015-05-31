# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.auth.models
import ecwsp.sis.models


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0004_auto_20150126_1540'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='faculty',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='student',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='emergencycontact',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='alt_email',
            field=models.EmailField(help_text=b'Alternative student email that is not their school email.', max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='parent_email',
            field=models.EmailField(max_length=254, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='userpreference',
            name='prefered_file_format',
            field=models.CharField(default=ecwsp.sis.models.get_prefered_format, help_text=b'Open Document Format is recommended.', max_length=b'1', verbose_name=b'Preferred file format', choices=[(b'o', b'Open Document Format (.odt, .ods)'), (b'm', b'Microsoft Binary (.doc, .xls)'), (b'x', b'Microsoft Office Open XML (.docx, .xlsx)')]),
        ),
        migrations.AlterField(
            model_name='userpreference',
            name='user',
            field=models.OneToOneField(editable=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
