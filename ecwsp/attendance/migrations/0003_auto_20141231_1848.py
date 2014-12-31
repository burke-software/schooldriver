# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_auto_20140716_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentattendance',
            name='student',
            field=models.ForeignKey(related_name='student_attn', to='sis.Student', help_text=b"Start typing a student's first or last name to search"),
            preserve_default=True,
        ),
    ]
