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
from decimal import Decimal, ROUND_HALF_UP

from ecwsp.sis.models import *
from ecwsp.schedule.models import *

MINOPERATOR_CHOICES = (
    (u'>', u'Greater than'),
    (u'>=', u'Greater than or equal to')
)
MAXOPERATOR_CHOICES = (
    (u'<=', u'Less than or equal to'),
    (u'<', u'Less than')
)

class Scale(models.Model):
    name = models.CharField(max_length=127)
    minimum = models.DecimalField(max_digits=8, decimal_places=2)
    maximum = models.DecimalField(max_digits=8, decimal_places=2)
    decimalPlaces = models.IntegerField(default=2)
    symbol = models.CharField(max_length=7, blank=True, null=True)
    def spruce(self, grade):
        try:
            decGrade = Decimal(str(grade)).quantize(10**(-1 * decimalPlaces), ROUND_HALF_UP)
        except InvalidOperation:
            # it's not a number, so leave it alone
            return grade
        for mapping in self.mapping_set.all():
            if mapping.applies(decGrade):
                return mapping.name
        return grade
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
    
class Item(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey('schedule.Course')
    date = models.DateField(auto_now=True)
    markingPeriod = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    category = models.ForeignKey('Category')
    scale = models.ForeignKey('Scale')
    multiplier = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    def __unicode__(self):
        return self.name + " (" + self.course.fullname + ")"

class Mark(models.Model):
    item = models.ForeignKey('Item')
    student = models.ForeignKey('sis.Student')
    mark = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    excused = models.BooleanField(default=False)
    # I haven't decided how I want to handle letter grades yet. TC never enters grades as letters.
    def __unicode__(self):
        return str(self.mark) + " - " + str(self.student) + "; " + str(self.item)
    
class Aggregate(models.Model):
    # come back interwebs,
    # so i can find a less ugly way to do this
    name = models.CharField(max_length=255)
    scale = models.ForeignKey('scale')
    singleStudent = models.ForeignKey('sis.Student', blank=True, null=True, related_name="single_student")
    student = models.ManyToManyField('sis.Student', blank=True, null=True)
    singleCourse = models.ForeignKey('schedule.Course', blank=True, null=True, related_name="single_course")
    course = models.ManyToManyField('schedule.Course', blank=True, null=True)
    singleCategory = models.ForeignKey('Category', blank=True, null=True, related_name="single_category")
    category = models.ManyToManyField('Category', blank=True, null=True)
    aggregate = models.ManyToManyField('self', blank=True, null=True)
    manualMark = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    # to do: deal with squashing to zero marks below a threshold
    def __unicode__(self):
        return self.name # not useful