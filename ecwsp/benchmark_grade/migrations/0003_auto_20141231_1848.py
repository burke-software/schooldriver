# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark_grade', '0002_auto_20140716_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculationrulecategoryascourse',
            name='calculation_rule',
            field=models.ForeignKey(related_name='category_as_course_set', to='benchmark_grade.CalculationRule'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='calculationrulepercoursecategory',
            name='calculation_rule',
            field=models.ForeignKey(related_name='per_course_category_set', to='benchmark_grade.CalculationRule'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='calculationrulesubstitution',
            name='calculation_rule',
            field=models.ForeignKey(related_name='substitution_set', to='benchmark_grade.CalculationRule'),
            preserve_default=True,
        ),
    ]
