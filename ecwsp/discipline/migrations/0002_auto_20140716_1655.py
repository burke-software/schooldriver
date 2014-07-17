# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discipline', '0001_initial'),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentdiscipline',
            name='students',
            field=models.ManyToManyField(to='sis.Student'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentdiscipline',
            name='teacher',
            field=models.ForeignKey(blank=True, to='sis.Faculty', null=True),
            preserve_default=True,
        ),
    ]
