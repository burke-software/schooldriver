# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('engrade_sync', '0002_auto_20140716_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teachersync',
            name='teacher',
            field=models.OneToOneField(to='sis.Faculty'),
        ),
    ]
