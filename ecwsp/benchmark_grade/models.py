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

class Scale(models.Model):
    name = models.CharField(max_length=127)
    minimum = models.DecimalField(max_digits=8, decimal_places=2)
    maximum = models.DecimalField(max_digits=8, decimal_places=2)
    decimalPlaces = models.IntegerField(default=2)
    symbol = models.CharField(max_length=7, blank=True)
    def spruce(self, grade):
        try:
            decGrade = Decimal(str(grade)).quantize(Decimal(str(10**(-1 * self.decimalPlaces))), ROUND_HALF_UP)
        except InvalidOperation:
            # it's not a number, so leave it alone
            return grade
        for mapping in self.mapping_set.all():
            if mapping.applies(decGrade):
                return mapping.name
        if self.symbol is not None:
            return str(decGrade) + self.symbol
        else:
            return str(decGrade)
    def range(self):
        s = str(self.minimum) + "-" + str(self.maximum)
        if self.symbol is not None:
            s += self.symbol
        return s
    def __unicode__(self):
        return self.name

class Mapping(models.Model):
    # what about substitutions of numbers for letter grades to allow averaging?
    name = models.CharField(max_length=127)
    scale = models.ForeignKey('Scale')
    minOperator = models.CharField(max_length=2, choices=MINOPERATOR_CHOICES)
    minimum = models.DecimalField(max_digits=8, decimal_places=2)
    maxOperator = models.CharField(max_length=2, choices=MAXOPERATOR_CHOICES)
    maximum = models.DecimalField(max_digits=8, decimal_places=2)
    def applies(self, grade):
        if self.minOperator == '>':
            def minCompare(n): return n > self.minimum
        if self.minOperator == '>=':
            def minCompare(n): return n >= self.minimum
        if self.maxOperator == '<':
            def maxCompare(n): return n < self.maximum
        if self.maxOperator == '<=':
            def maxCompare(n): return n <= self.maximum
        # to do: raise an exception if the operator isn't valid
        return minCompare(grade) and maxCompare(grade)
    def __unicode__(self):
        return self.name + " (" + self.scale.name + ")"
    class Meta: # this isn't really enough to keep grossness away
        unique_together = ("name", "scale")
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=1)
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
    markingPeriod = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    @property
    def marking_period(self): return self.markingPeriod # need to get with the naming convention
    category = models.ForeignKey('Category')
    scale = models.ForeignKey('Scale', blank=True, null=True) # this is going away
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
    scale = models.ForeignKey('Scale')
    manualMark = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    cachedValue = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    singleStudent = models.ForeignKey('sis.Student', blank=True, null=True, related_name="single_student")
    student = models.ManyToManyField('sis.Student', blank=True, null=True)
    singleCourse = models.ForeignKey('schedule.Course', blank=True, null=True, related_name="single_course")
    course = models.ManyToManyField('schedule.Course', blank=True, null=True)
    singleCategory = models.ForeignKey('Category', blank=True, null=True, related_name="single_category")
    category = models.ManyToManyField('Category', blank=True, null=True)
    aggregate = models.ManyToManyField('self', blank=True, null=True)
    singleMarkingPeriod = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    points_possible = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    # rudimentary for now
    # no m2m, multipliers
    # also untested
    def max(self, normalize=False, markDescription=None):
        highest = None
        items = Item.objects.filter(course=self.singleCourse, category=self.singleCategory, markingPeriod=self.singleMarkingPeriod)
        for item in items:
            if markDescription is not None:
                marks = Mark.objects.filter(item=item, student=self.singleStudent, description=markDescription)
            else:
                marks = Mark.objects.filter(item=item, student=self.singleStudent)
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
    def min(self, normalize=False, markDescription=None):
        lowest = None
        items = Item.objects.filter(course=self.singleCourse, category=self.singleCategory, markingPeriod=self.singleMarkingPeriod)
        for item in items:
            if markDescription is not None:
                marks = Mark.objects.filter(item=item, student=self.singleStudent, description=markDescription)
            else:
                marks = Mark.objects.filter(item=item, student=self.singleStudent)
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
    def mean(self, normalize=False, markDescription=None):
        numerator = 0
        denominator = 0
        items = Item.objects.filter(course=self.singleCourse, category=self.singleCategory, markingPeriod=self.singleMarkingPeriod)
        for item in items:
            if markDescription is not None:
                marks = Mark.objects.filter(item=item, student=self.singleStudent, description=markDescription)
            else:
                marks = Mark.objects.filter(item=item, student=self.singleStudent)
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
