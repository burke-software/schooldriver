# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20140716_1655'),
        ('benchmarks', '0002_auto_20140716_1655'),
        ('benchmark_grade', '0001_initial'),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aggregate',
            name='course_section',
            field=models.ForeignKey(blank=True, to='schedule.CourseSection', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aggregate',
            name='marking_period',
            field=models.ForeignKey(blank=True, to='schedule.MarkingPeriod', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aggregate',
            name='student',
            field=models.ForeignKey(blank=True, to='sis.Student', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='AggregateTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_id', models.CharField(max_length=36)),
                ('timestamp', models.DateTimeField(default=datetime.datetime.now)),
                ('aggregate', models.ForeignKey(to='benchmark_grade.Aggregate')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='aggregatetask',
            unique_together=set([(b'aggregate', b'task_id')]),
        ),
        migrations.CreateModel(
            name='AssignmentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalculationRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('points_possible', models.DecimalField(default=4, max_digits=8, decimal_places=2)),
                ('decimal_places', models.IntegerField(default=2)),
                ('first_year_effective', models.ForeignKey(to='sis.SchoolYear', help_text=b'Rule also applies to subsequent years unless a more recent rule exists.', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalculationRuleCategoryAsCourse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('calculation_rule', models.ForeignKey(to='benchmark_grade.CalculationRule')),
                ('include_departments', models.ManyToManyField(to='schedule.Department', null=True, blank=True)),
                ('special_course_section', models.ForeignKey(help_text=b' Grades for this course section will be OVERWRITTEN by the\n        category averages! ', to='schedule.CourseSection')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalculationRulePerCourseCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.DecimalField(default=1, max_digits=5, decimal_places=4)),
                ('apply_to_departments', models.ManyToManyField(to='schedule.Department', null=True, blank=True)),
                ('calculation_rule', models.ForeignKey(to='benchmark_grade.CalculationRule')),
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
                ('match_value', models.DecimalField(help_text=b'Use only (0..1) unless category has fixed points possible.', max_digits=8, decimal_places=2)),
                ('display_as', models.CharField(max_length=16, null=True, blank=True)),
                ('calculate_as', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('flag_visually', models.BooleanField(default=False)),
                ('apply_to_departments', models.ManyToManyField(to='schedule.Department', null=True, blank=True)),
                ('calculation_rule', models.ForeignKey(to='benchmark_grade.CalculationRule')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('allow_multiple_demonstrations', models.BooleanField(default=False)),
                ('demonstration_aggregation_method', models.CharField(blank=True, max_length=16, null=True, choices=[('Avg', 'Average'), ('Count', 'Count'), ('Max', 'Maximum'), ('Min', 'Minimum'), ('StdDev', 'Standard deviation'), ('Sum', 'Sum'), ('Variance', 'Variance')])),
                ('display_in_gradebook', models.BooleanField(default=True)),
                ('fixed_points_possible', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('fixed_granularity', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('display_order', models.IntegerField(unique=True, null=True, blank=True)),
                ('display_scale', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('display_symbol', models.CharField(max_length=7, null=True, blank=True)),
            ],
            options={
                'ordering': [b'display_order'],
                'verbose_name_plural': b'categories',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='calculationrulesubstitution',
            name='apply_to_categories',
            field=models.ManyToManyField(to='benchmark_grade.Category', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='calculationrulepercoursecategory',
            name='category',
            field=models.ForeignKey(to='benchmark_grade.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='calculationrulecategoryascourse',
            name='category',
            field=models.ForeignKey(to='benchmark_grade.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aggregate',
            name='category',
            field=models.ForeignKey(blank=True, to='benchmark_grade.Category', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='aggregate',
            unique_together=set([(b'student', b'course_section', b'category', b'marking_period')]),
        ),
        migrations.CreateModel(
            name='Demonstration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('points_possible', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('multiplier', models.DecimalField(default=1, max_digits=8, decimal_places=2)),
                ('assignment_type', models.ForeignKey(blank=True, to='benchmark_grade.AssignmentType', null=True)),
                ('benchmark', models.ForeignKey(verbose_name=b'standard', blank=True, to='benchmarks.Benchmark', null=True)),
                ('category', models.ForeignKey(to='benchmark_grade.Category')),
                ('course_section', models.ForeignKey(to='schedule.CourseSection')),
                ('marking_period', models.ForeignKey(blank=True, to='schedule.MarkingPeriod', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='demonstration',
            name='item',
            field=models.ForeignKey(to='benchmark_grade.Item'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mark', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('normalized_mark', models.FloatField(null=True, blank=True)),
                ('letter_grade', models.CharField(help_text=b'Overrides numerical mark.', max_length=3, null=True, blank=True)),
                ('demonstration', models.ForeignKey(blank=True, to='benchmark_grade.Demonstration', null=True)),
                ('item', models.ForeignKey(to='benchmark_grade.Item')),
                ('student', models.ForeignKey(to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mark',
            unique_together=set([(b'item', b'demonstration', b'student')]),
        ),
    ]
