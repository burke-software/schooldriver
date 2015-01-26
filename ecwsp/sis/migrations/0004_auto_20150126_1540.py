# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0003_auto_20140717_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emergencycontact',
            name='email',
            field=models.EmailField(default='', max_length=75, blank=True),
            preserve_default=False,
        ),
    ]
