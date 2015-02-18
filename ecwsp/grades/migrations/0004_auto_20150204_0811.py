# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0003_grade_enrollment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='letter_grade',
            field=models.CharField(blank=True, max_length=10, null=True, help_text=b'Will override grade.', choices=[(b'I', b'Incomplete'), (b'P', b'Pass'), (b'F', b'Fail'), (b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'HP', b'High Pass'), (b'LP', b'Low Pass'), (b'M', b'Missing')]),
            preserve_default=True,
        ),
    ]
