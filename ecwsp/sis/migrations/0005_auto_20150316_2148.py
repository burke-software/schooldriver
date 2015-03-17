# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ecwsp.sis.models


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0004_auto_20150126_1540'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='cached_gpa',
        ),
        migrations.RemoveField(
            model_name='student',
            name='gpa_recalculation_needed',
        ),
        migrations.AlterField(
            model_name='userpreference',
            name='prefered_file_format',
            field=models.CharField(default=ecwsp.sis.models.get_prefered_format, help_text=b'Open Document Format is recommended.', max_length=b'1', verbose_name=b'Preferred file format', choices=[(b'o', b'Open Document Format (.odt, .ods)'), (b'm', b'Microsoft Binary (.doc, .xls)'), (b'x', b'Microsoft Office Open XML (.docx, .xlsx)')]),
            preserve_default=True,
        ),
    ]
