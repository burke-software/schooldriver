#   Copyright 2013 Burke Software and Consulting LLC
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
from django.db.models import Avg, Count, Max, Min, StdDev, Sum, Variance
#from django.contrib.localflavor.us.models import *
from django.conf import settings
from decimal import Decimal
from datetime import datetime

####### TURN ME INTO A MANAGER #######
def benchmark_find_calculation_rule(school_year):
    rules = CalculationRule.objects.filter(first_year_effective=school_year)
    if rules:
        # We have a rule explicitly matching this marking period's school year
        rule = rules[0]
    else:
        # No explicit match, so find the most recent rule that went into effect *before* this marking period's school year
        rules = CalculationRule.objects.filter(first_year_effective__start_date__lt=school_year.start_date).order_by('-first_year_effective__start_date')
        if rules:
            rule = rules[0]
        elif CalculationRule.objects.count() == 0 and Category.objects.count() <= 1:
            # The school hasn't configured anything; cut them some slack
            rule = CalculationRule.objects.get_or_create(first_year_effective = school_year)[0]
            if Category.objects.count() == 1:
                category = Category.objects.all()[0]
            else:
                category = Category.objects.get_or_create(name="Everything")[0]
            per_course_category = CalculationRulePerCourseCategory.objects.get_or_create(calculation_rule=rule, category=category)[0]
            per_course_category.apply_to_departments.add(*Department.objects.all())
        else:
            # The school has touched the configuration; don't guess at what they want
            raise Exception('There is no suitable calculation rule for the school year {}.'.format(school_year))
    return rule
######################################

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

AGGREGATE_METHODS = (
    (u'Avg', u'Average'),
    (u'Count', u'Count'),
    (u'Max', u'Maximum'),
    (u'Min', u'Minimum'),
    (u'StdDev', u'Standard deviation'),
    (u'Sum', u'Sum'),
    (u'Variance', u'Variance')
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
        raise Exception('CalculationRuleSubstitution with id={} has invalid operator.'.format(self.pk))

class Category(models.Model):
    name = models.CharField(max_length=255)
    allow_multiple_demonstrations = models.BooleanField(default=False)
    demonstration_aggregation_method = models.CharField(max_length=16, choices=AGGREGATE_METHODS, blank=True, null=True)
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
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.allow_multiple_demonstrations and self.demonstration_aggregation_method is None:
            raise ValidationError('Please select a demonstration aggregation method.')
        if not self.allow_multiple_demonstrations and self.demonstration_aggregation_method is not None:
            self.demonstration_aggregation_method = None
    @property
    def aggregation_method(self):
        if self.demonstration_aggregation_method == 'Avg':
            return Avg
        if self.demonstration_aggregation_method == 'Count':
            return Count
        if self.demonstration_aggregation_method == 'Max':
            return Max
        if self.demonstration_aggregation_method == 'Min':
            return Min
        if self.demonstration_aggregation_method == 'StdDev':
            return StdDev
        if self.demonstration_aggregation_method == 'Sum':
            return Sum
        if self.demonstration_aggregation_method == 'Variance':
            return Variance
        raise Exception('Category with id={} has invalid aggregation method.'.format(self.pk))

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
        if not self.points_possible > 0:
            # TODO: DB validation once TC cleans up their mess
            raise ValidationError("Please assign a number of points possible greater than zero.")
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
    @property
    def mark_set(self):
        ''' All the Marks needed to calculate this Aggregate '''
        item_fields = ('course', 'category', 'marking_period')
        criteria = {'student_id': self.student.pk}
        for field in item_fields:
            field += '_id'
            criterium = getattr(self, field)
            if criterium is not None:
                criteria['item__' + field] = criterium
        return Mark.objects.filter(**criteria).exclude(mark=None)
    def mark_values_list(self, normalize=False):
        ''' A list of tuples of (mark, points_possible) for all the Marks
        needed to calculate this Aggregate '''
        if self.category is not None and self.category.allow_multiple_demonstrations:
            if normalize:
                mark_list = self.mark_set.values('item')\
                        .annotate(self.category.aggregation_method('normalized_mark'))\
                        .values_list('normalized_mark__max')
                return [(x[0], 1) for x in mark_list]
            else:
                return self.mark_set.values('item')\
                        .annotate(self.category.aggregation_method('mark'))\
                        .values_list('mark__max', 'item__points_possible')
        else:
            if normalize:
                mark_list = self.mark_set.values_list('normalized_mark')
                return [(x[0], 1) for x in mark_list]
            else:
                return self.mark_set.values_list('mark', 'item__points_possible')
    def depends_on(self):
        ''' Returns all Aggregates, in the form of [(Aggregate, created),], immediately required to calculate
        this Aggregate. Not recursive; multiple levels of dependency are NOT considered. '''
        aggregate_tuples = []
        ours = [self.student_id, self.course_id,
                self.category_id, self.marking_period_id]
        ours = [x is not None for x in ours]
        if ours == [True, True, True, True]:
            ''' As specific as it gets. Average for one category
            in one course during one marking period. '''
            return aggregate_tuples
        #if ours == [True, True, True, False]:
            # Not currently used
        if ours == [True, True, False, True]:
            ''' Course grade for one marking period. '''
            rule = benchmark_find_calculation_rule(self.marking_period.school_year)
            per_course_categories = rule.per_course_category_set.filter(apply_to_departments=self.course.department)
            for per_course_category in per_course_categories:
                aggregate_tuples.append(Aggregate.objects.get_or_create(student_id=self.student_id,
                    course_id=self.course_id, category_id=per_course_category.category_id,
                    marking_period_id=self.marking_period_id))
            return aggregate_tuples
        if ours == [True, True, False, False]:
            ''' Overall course grade, for the entire duration of the course. '''
            marking_periods = self.course.marking_period.all()
            for marking_period in marking_periods:
                aggregate_tuples.append(Aggregate.objects.get_or_create(student_id=self.student_id,
                    course_id=self.course_id, category_id=None, marking_period_id=marking_period.pk))
            return aggregate_tuples
        if ours == [True, False, True, True]:
            ''' Average of a category across all courses for one marking period.
            TC used this last year and counted it in GPAs as if it were a course. '''
            rule = benchmark_find_calculation_rule(self.marking_period.school_year)
            departments = rule.category_as_course_set.get(category_id=self.category_id).include_departments.all()
            courses = self.student.course_set.filter(marking_period=self.marking_period_id,
                department__in=departments, graded=True)
            for course in courses:
                aggregate_tuples.append(Aggregate.objects.get_or_create(student_id=self.student_id,
                    course_id=course.pk, category_id=self.category_id, marking_period_id=self.marking_period_id))
            return aggregate_tuples
        raise Exception("Aggregate type unrecognized.")
    def max(self):
        if self.points_possible is None:
            return None
        mark, item_points_possible = zip(*self.mark_values_list(normalize=True))
        if len(mark):
            return Decimal(max(mark)) * self.points_possible
        else:
            return None
    def min(self):
        if self.points_possible is None:
            return None
        mark, item_points_possible = zip(*self.mark_values_list(normalize=True))
        if len(mark):
            return Decimal(min(mark)) * self.points_possible
        else:
            return None
    def mean(self, normalize=False):
        if self.points_possible is None:
            return None
        mark, item_points_possible = zip(*self.mark_values_list(normalize))
        total_points_possible = sum(item_points_possible)
        if total_points_possible:
            return Decimal(sum(mark) / total_points_possible) * self.points_possible
        
    def __unicode__(self):
        return self.name # not useful

class AggregateTask(models.Model):
    ''' A Celery task in the process of recalculating an Aggregate '''
    aggregate = models.ForeignKey('Aggregate')
    task_id = models.CharField(max_length=36)
    timestamp = models.DateTimeField(default=datetime.now)
    class Meta:
        unique_together = ('aggregate', 'task_id')
