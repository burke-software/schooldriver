#   Copyright 2011 Burke Software and Consulting LLC
#   Author: John Milner <john@tmoj.net>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#     
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#      
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from django.db import models
from django.db.models import Min, Max, Sum, Avg
#from django.contrib.localflavor.us.models import *
from django.conf import settings
from decimal import Decimal
from datetime import datetime

from django.core.exceptions import ImproperlyConfigured
if not 'ecwsp.benchmarks' in settings.INSTALLED_APPS:
    raise ImproperlyConfigured('benchmark_grade depends on benchmarks but it is not in installed apps')

OPERATOR_CHOICES = (
    (u'>', u'Greater than'),
    (u'>=', u'Greater than or equal to'),
    (u'<=', u'Less than or equal to'),
    (u'<', u'Less than'),
    (u'!=', u'Not equal to'),
    (u'==', u'Equal to')
)

class CalculationRule(models.Model):
    ''' A per-year GPA calculation rule. It should also be applied to future years unless a more current rule exists.
    '''
    # Potential calculation components: career, year, marking period, course
    first_year_effective = models.ForeignKey('sis.SchoolYear', unique=True, help_text='Rule also applies to subsequent years unless a more recent rule exists.')
    points_possible = models.DecimalField(max_digits=8, decimal_places=2, default=4)
    decimal_places = models.IntegerField(default=2)

    def substitute(self, item, value):
        calculate_as = value
        display_as = None
        for s in self.substitution_set.filter(apply_to_departments=item.course.department, apply_to_categories=item.category):
            if s.applies_to(value):
                if s.calculate_as is not None:
                    calculate_as = s.calculate_as
                if s.display_as is not None and len(s.display_as):
                    display_as = s.display_as
                return calculate_as, display_as
        return calculate_as, display_as

    def __unicode__(self):
        return u'Rule of ' + self.first_year_effective.name

class CalculationRulePerCourseCategory(models.Model):
    ''' A weight assignment for a category within each course.
    '''
    category = models.ForeignKey('Category')
    weight = models.DecimalField(max_digits=5, decimal_places=4, default=1)
    apply_to_departments = models.ManyToManyField('schedule.Department', blank=True, null=True)
    calculation_rule = models.ForeignKey('CalculationRule', related_name='per_course_category_set')

class CalculationRuleCategoryAsCourse(models.Model):
    ''' A category whose average is given the same weight as a course in a marking period's average
    '''
    category = models.ForeignKey('Category')
    include_departments = models.ManyToManyField('schedule.Department', blank=True, null=True)
    calculation_rule = models.ForeignKey('CalculationRule', related_name='category_as_course_set')

class CalculationRuleSubstitution(models.Model):
    operator = models.CharField(max_length=2, choices=OPERATOR_CHOICES)
    match_value = models.DecimalField(max_digits=8, decimal_places=2)
    display_as = models.CharField(max_length=16, blank=True, null=True)
    calculate_as = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    flag_visually = models.BooleanField(default=False)
    apply_to_departments = models.ManyToManyField('schedule.Department', blank=True, null=True)
    apply_to_categories = models.ManyToManyField('Category', blank=True, null=True)
    calculation_rule = models.ForeignKey('CalculationRule', related_name='substitution_set')
    def applies_to(self, value):
        if self.operator == '>':
            return value > self.match_value
        if self.operator == '>=':
            return value >= self.match_value
        if self.operator == '<=':
            return value <= self.match_value
        if self.operator == '<':
            return value < self.match_value
        if self.operator == '!=':
            return value != self.match_value
        if self.operator == '==':
            return value == self.match_value
        raise Exception('CalculationRuleSubstitution with id={} has invalid operator.'.format(self.id))

class Category(models.Model):
    name = models.CharField(max_length=255)
    allow_multiple_demonstrations = models.BooleanField(default=False)
    display_in_gradebook = models.BooleanField(default=True)
    fixed_points_possible = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    fixed_granularity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    display_order = models.IntegerField(unique=True, blank=True, null=True)
    display_scale = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    display_symbol = models.CharField(max_length=7, blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['display_order']

class AssignmentType(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name
    
class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    course = models.ForeignKey('schedule.Course')
    date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    marking_period = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    category = models.ForeignKey('Category')
    points_possible = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    assignment_type = models.ForeignKey('AssignmentType', blank=True, null=True)
    benchmark = models.ForeignKey('benchmarks.Benchmark', blank=True, null=True, verbose_name='standard')
    
    @property
    def benchmark_description(self): return self.benchmark.name
    multiplier = models.DecimalField(max_digits=8, decimal_places=2, default=1) # not used yet
    def clean(self):
        from django.core.exceptions import ValidationError
        # must use hasattr when checking if non-nullable field is null
        # http://stackoverflow.com/q/5725065
        if hasattr(self, 'category') and self.category.fixed_points_possible is not None:
            if self.points_possible is not None:
                if self.points_possible != self.category.fixed_points_possible:
                    raise ValidationError("This item's category, {}, requires {} possible points.".format(self.category, self.category.fixed_points_possible))
            else:
                # let people get away with leaving it blank
                self.points_possible = self.category.fixed_points_possible
    def __unicode__(self):
        if self.benchmark:
            benchmark_number = self.benchmark.number
        else:
            benchmark_number = None
        latter = u', '.join(map(unicode, filter(None, (benchmark_number, self.description))))
        return u': '.join(map(unicode, filter(None, (self.name, latter))))

class Demonstration(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    item = models.ForeignKey('Item')
    def __unicode__(self):
        return self.name + u' - ' + unicode(self.item)

class Mark(models.Model):
    item = models.ForeignKey('Item')
    demonstration = models.ForeignKey('Demonstration', blank=True, null=True)
    student = models.ForeignKey('sis.Student')
    mark = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    normalized_mark = models.FloatField(blank=True, null=True)
    
    class Meta:
        unique_together = ('item', 'demonstration', 'student',)
    
    
    # I haven't decided how I want to handle letter grades yet. TC never enters grades as letters.
    def save(self, *args, **kwargs):
        if self.mark is not None and self.item.points_possible is not None:
            # ideally, store a value between 0 and 1, but that only happens if 0 <= self.mark <= self.item.points_possible
            # in practice, people set marks that far exceed points_possible
            self.normalized_mark = float(self.mark) / float(self.item.points_possible)
        super(Mark, self).save(*args, **kwargs)
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.item.category.fixed_granularity and self.mark and self.mark % self.item.category.fixed_granularity != 0:
            raise ValidationError('Mark does not conform to fixed granularity of {}.'.format(self.item.category.fixed_granularity))
    def __unicode__(self):
        return unicode(self.mark) + u' - ' + unicode(self.student) + u'; ' + unicode(self.item)
    
class Aggregate(models.Model):
    name = models.CharField(max_length=255)
    manual_mark = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    cached_value = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    cached_substitution = models.CharField(max_length=16, blank=True, null=True)
    student = models.ForeignKey('sis.Student', blank=True, null=True)
    course = models.ForeignKey('schedule.Course', blank=True, null=True)
    category = models.ForeignKey('Category', blank=True, null=True)
    marking_period = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    points_possible = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'course', 'category', 'marking_period')
    
    
    def max(self):
        if self.points_possible is None:
            return None
        items = Item.objects.filter(course=self.course, category=self.category, marking_period=self.marking_period)
        marks = Mark.objects.filter(item__in=items, student=self.student).exclude(normalized_mark=None)
        if not marks:
            return None
        highest = marks.aggregate(Max('normalized_mark'))['normalized_mark__max']
        highest *= self.points_possible
        return highest

    def min(self):
        if self.points_possible is None:
            return None
        items = Item.objects.filter(course=self.course, category=self.category, marking_period=self.marking_period)
        marks = Mark.objects.filter(item__in=items, student=self.student).exclude(normalized_mark=None)
        if not marks:
            return None
        lowest = marks.aggregate(Min('normalized_mark'))['normalized_mark__min']
        lowest *= self.points_possible
        return lowest

    def mean(self, normalize=False):
        if self.points_possible is None:
            return None
        items = Item.objects.filter(course=self.course, category=self.category, marking_period=self.marking_period)
        if normalize: # mark should always == normalized_mark, but meh
            marks = Mark.objects.filter(item__in=items, student=self.student).exclude(normalized_mark=None)
        else:
            marks = Mark.objects.filter(item__in=items, student=self.student).exclude(mark=None)
        if not marks:
            return None
        if normalize:
            mean = Decimal(marks.aggregate(Avg('normalized_mark'))['normalized_mark__avg']) # angry that the DB/ORM returns a float
        else:
            numerator = marks.aggregate(Sum('mark'))['mark__sum']
            denominator = marks.aggregate(Sum('item__points_possible'))['item__points_possible__sum']
            if denominator == 0:
                return None
            mean = numerator / denominator
        mean *= self.points_possible
        return mean
        
    def __unicode__(self):
        return self.name # not useful

class AggregateTask(models.Model):
    ''' A Celery task in the process of recalculating an Aggregate '''
    aggregate = models.ForeignKey('Aggregate')
    task_id = models.CharField(max_length=36)
    timestamp = models.DateTimeField(default=datetime.now)
    class Meta:
        unique_together = ('aggregate', 'task_id')
