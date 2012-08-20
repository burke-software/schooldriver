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
from django.contrib.localflavor.us.models import *
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from ecwsp.sis.models import *
from ecwsp.schedule.models import *
from ecwsp.omr.models import Benchmark

import sys

MINOPERATOR_CHOICES = (
    (u'>', u'Greater than'),
    (u'>=', u'Greater than or equal to')
)
MAXOPERATOR_CHOICES = (
    (u'<=', u'Less than or equal to'),
    (u'<', u'Less than')
)


class CalculationRule(models.Model):
    ''' A per-year GPA calculation rule. It should also be applied to future years unless a more current rule exists.
    '''
    # Potential calculation components: career, year, marking period, course
    first_year_effective = models.ForeignKey('sis.SchoolYear', help_text='Rule also applies to subsequent years unless a more recent rule exists.')
    points_possible = models.DecimalField(max_digits=8, decimal_places=2, default=4)
    decimal_places = models.IntegerField(default=2)
    
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

class Category(models.Model):
    name = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    display_in_gradebook = models.BooleanField(default=True)
    # some categories will be school-wide.
    # to do: search courses' individual categories first, then the global ones.
    course = models.ForeignKey('schedule.Course', blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = "categories"

class AssignmentType(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name
    
class Item(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey('schedule.Course')
    date = models.DateField(blank=True, null=True)
    marking_period = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    category = models.ForeignKey('Category')
    #scale = models.ForeignKey('Scale', blank=True, null=True) # this is going away
    points_possible = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    assignment_type = models.ForeignKey('AssignmentType', blank=True, null=True)
    benchmark = models.ForeignKey('omr.Benchmark', blank=True, null=True, verbose_name='standard')
    @property
    def benchmark_description(self): return self.benchmark.name
    multiplier = models.DecimalField(max_digits=8, decimal_places=2, default=1) # not used yet
    def __unicode__(self):
        return self.name + " - " + self.category.name + " (" + self.course.fullname + ")"


class Mark(models.Model):
    item = models.ForeignKey('Item')
    student = models.ForeignKey('sis.Student')
    mark = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    description = models.CharField(max_length=255)
    excused = models.BooleanField(default=False)
    # I haven't decided how I want to handle letter grades yet. TC never enters grades as letters.
    def __unicode__(self):
        return unicode(self.mark) + u' - ' + unicode(self.student) + u'; ' + unicode(self.item)
    
class Aggregate(models.Model):
    # come back interwebs,
    # so i can find a less ugly way to do this
    name = models.CharField(max_length=255)
    #scale = models.ForeignKey('Scale', blank=True, null=True)
    manual_mark = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    cached_value = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    student = models.ForeignKey('sis.Student', blank=True, null=True)
    course = models.ForeignKey('schedule.Course', blank=True, null=True)
    category = models.ForeignKey('Category', blank=True, null=True)
    marking_period = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    points_possible = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    # rudimentary for now
    # no m2m, multipliers
    # also untested
    def max(self, normalize=False, mark_description=None):
        highest = None
        items = Item.objects.filter(course=self.course, category=self.category, marking_period=self.marking_period)
        for item in items:
            if mark_description is not None:
                marks = Mark.objects.filter(item=item, student=self.student, description=mark_description)
            else:
                marks = Mark.objects.filter(item=item, student=self.student)
            for mark in marks:
                if normalize:
                    # score between 0 and 1
                    unscaled = (mark.mark - mark.item.scale.minimum) / (mark.item.scale.maximum - mark.item.scale.minimum)
                    if highest is None or unscaled > highest:
                        highest = unscaled
                else:
                    if highest is None or mark.mark > highest:
                        highest = mark.mark
        if normalize:
            highest = highest * (self.scale.maximum - self.scale.minimum) + self.scale.minimum
        if highest is None:
            return None
        else:
            return Decimal(str(highest))
    def min(self, normalize=False, mark_description=None):
        lowest = None
        items = Item.objects.filter(course=self.course, category=self.category, marking_period=self.marking_period)
        for item in items:
            if mark_description is not None:
                marks = Mark.objects.filter(item=item, student=self.student, description=mark_description)
            else:
                marks = Mark.objects.filter(item=item, student=self.student)
            for mark in marks:
                if normalize:
                    # score between 0 and 1
                    unscaled = (mark.mark - mark.item.scale.minimum) / (mark.item.scale.maximum - mark.item.scale.minimum)
                    if lowest is None or unscaled < lowest:
                        lowest = unscaled
                else:
                    if lowest is None or mark.mark < lowest:
                        lowest = mark.mark
        if normalize:                        
            lowest = lowest * (self.scale.maximum - self.scale.minimum) + self.scale.minimum
        if lowest is None:
            return None
        else:
            return Decimal(str(lowest))
    def mean(self, normalize=False, mark_description=None):
        numerator = 0
        denominator = 0
        items = Item.objects.filter(course=self.course, category=self.category, marking_period=self.marking_period)
        for item in items:
            if mark_description is not None:
                marks = Mark.objects.filter(item=item, student=self.student, description=mark_description)
            else:
                marks = Mark.objects.filter(item=item, student=self.student)
            for mark in marks:
                if normalize:
                    # score between 0 and 1
                    unscaled = (mark.mark - mark.item.scale.minimum) / (mark.item.scale.maximum - mark.item.scale.minimum)
                    numerator += unscaled
                    denominator += 1
                else:
                    numerator += mark.mark
                    denominator += mark.item.scale.maximum
        if denominator == 0:
            return None
        result = numerator / denominator
        result = result * (self.scale.maximum - self.scale.minimum) + self.scale.minimum
        return Decimal(str(result))
        
    # to do: deal with squashing to zero marks below a threshold
    def __unicode__(self):
        return self.name # not useful
