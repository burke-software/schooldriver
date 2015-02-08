# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import ecwsp.gradebook.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0003_auto_20140717_1002'),
        ('benchmarks', '0003_auto_20141231_1848'),
        ('schedule', '0004_auto_20150102_1238'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('points_possible', ecwsp.gradebook.models.GradeField(null=True, max_digits=8, decimal_places=2, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AssignmentCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('allow_multiple_demonstrations', models.BooleanField(default=False)),
                ('demonstration_aggregation_method', models.CharField(blank=True, max_length=16, null=True, choices=[('Avg', 'Average'), ('Count', 'Count'), ('Max', 'Maximum'), ('Min', 'Minimum'), ('StdDev', 'Standard deviation'), ('Sum', 'Sum'), ('Variance', 'Variance')])),
                ('display_in_gradebook', models.BooleanField(default=True)),
                ('fixed_points_possible', ecwsp.gradebook.models.GradeField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('fixed_granularity', ecwsp.gradebook.models.GradeField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('display_order', models.IntegerField(unique=True, null=True, blank=True)),
                ('display_scale', ecwsp.gradebook.models.GradeField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('display_symbol', models.CharField(max_length=7, null=True, blank=True)),
            ],
            options={
                'ordering': ['display_order'],
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AssignmentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('weight', ecwsp.gradebook.models.WeightField(default=1, max_digits=5, decimal_places=4)),
                ('is_default', models.BooleanField(default=False)),
                ('teacher', models.ForeignKey(blank=True, to='sis.Faculty', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalculationRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('points_possible', ecwsp.gradebook.models.GradeField(decimal_places=2, default=100, max_digits=8, blank=True, help_text=b'A teachergradebook is out of this many points. Or the max possible points a student can earn. Common examples are 100 or 4.0.', null=True)),
                ('decimal_places', models.IntegerField(default=2)),
                ('first_year_effective', models.ForeignKey(related_name='gradebook_calculationrule_set', to='sis.SchoolYear', help_text=b'Rule also applies to subsequent years.', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalculationRulePerCourseCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', ecwsp.gradebook.models.WeightField(default=1, max_digits=5, decimal_places=4)),
                ('apply_to_departments', models.ManyToManyField(related_name='gradebook_calculationrulepercoursecategory_set', null=True, to='schedule.Department', blank=True)),
                ('calculation_rule', models.ForeignKey(related_name='per_course_category_set', to='gradebook.CalculationRule')),
                ('category', models.ForeignKey(to='gradebook.AssignmentCategory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalculationRuleSubstitution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operator', models.CharField(max_length=2, choices=[('>', 'Greater than'), ('>=', 'Greater than or equal to'), ('<=', 'Less than or equal to'), ('<', 'Less than'), ('!=', 'Not equal to'), ('==', 'Equal to')])),
                ('match_value', ecwsp.gradebook.models.GradeField(help_text=b'Use only (0..1) unless category has fixed points possible.', null=True, max_digits=8, decimal_places=2, blank=True)),
                ('display_as', models.CharField(max_length=16, null=True, blank=True)),
                ('calculate_as', ecwsp.gradebook.models.GradeField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('flag_visually', models.BooleanField(default=False)),
                ('apply_to_categories', models.ManyToManyField(to='gradebook.AssignmentCategory', null=True, blank=True)),
                ('apply_to_departments', models.ManyToManyField(related_name='+', null=True, to='schedule.Department', blank=True)),
                ('calculation_rule', models.ForeignKey(related_name='substitution_set', to='gradebook.CalculationRule')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Demonstration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('assignment', models.ForeignKey(to='gradebook.Assignment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mark', ecwsp.gradebook.models.GradeField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('normalized_mark', models.FloatField(null=True, blank=True)),
                ('letter_grade', models.CharField(help_text=b'Overrides numerical mark.', max_length=3, null=True, blank=True)),
                ('assignment', models.ForeignKey(to='gradebook.Assignment')),
                ('demonstration', models.ForeignKey(blank=True, to='gradebook.Demonstration', null=True)),
                ('student', models.ForeignKey(related_name='gradebook_mark_set', to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mark',
            unique_together=set([('assignment', 'demonstration', 'student')]),
        ),
        migrations.AddField(
            model_name='assignment',
            name='assignment_type',
            field=models.ForeignKey(blank=True, to='gradebook.AssignmentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assignment',
            name='benchmark',
            field=models.ForeignKey(verbose_name=b'standard', blank=True, to='benchmarks.Benchmark', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assignment',
            name='category',
            field=models.ForeignKey(blank=True, to='gradebook.AssignmentCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assignment',
            name='course_section',
            field=models.ForeignKey(to='schedule.CourseSection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assignment',
            name='marking_period',
            field=models.ForeignKey(blank=True, to='schedule.MarkingPeriod', null=True),
            preserve_default=True,
        ),
    ]
