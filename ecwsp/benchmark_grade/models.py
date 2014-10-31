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
from django.conf import settings
from decimal import Decimal, InvalidOperation
from datetime import datetime
from ecwsp.grades.models import Grade
import logging

from django.core.exceptions import ImproperlyConfigured
if not 'ecwsp.benchmarks' in settings.INSTALLED_APPS:
    raise ImproperlyConfigured('benchmark_grade depends on benchmarks but it is not in installed apps')

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

# Manage the DB better and get rid of these #
def benchmark_get_create_or_flush(model_base_or_set, **kwargs):
    ''' make sure there is one and only one object matching our criteria '''

    # How does it quack?
    try:
        manager = model_base_or_set.objects
    except AttributeError:
        manager = model_base_or_set

    try:
        model, created = manager.get_or_create(**kwargs)
    except manager.model.MultipleObjectsReturned:
        # unsure why this happens, but it does
        bad = manager.filter(**kwargs)
        logging.error('Expected 0 or 1 {} but found {}; flushing them all!'.format(str(manager.model).split("'")[1], bad.count()), exc_info=True)
        bad.delete()
        model, created = manager.get_or_create(**kwargs)
    return model, created

def benchmark_get_or_flush(model_base_or_set, **kwargs):
    ''' make sure there is at most one object matching our criteria
    if there are two or more, don't try to guess at the correct one; just delete them '''

    # How does it quack?
    try:
        manager = model_base_or_set.objects
    except AttributeError:
        manager = model_base_or_set

    try:
        model = manager.get(**kwargs)
    except manager.model.MultipleObjectsReturned:
        # unsure why this happens, but it does
        bad = manager.filter(**kwargs)
        logging.error('Expected 1 {} but found {}; flushing them all!'.format(str(manager.model).split("'")[1], bad.count()), exc_info=True)
        bad.delete()
        raise manager.model.DoesNotExist
    return model
#############################################

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
    # Potential calculation components: career, year, marking period, course section
    first_year_effective = models.ForeignKey('sis.SchoolYear', unique=True, help_text='Rule also applies to subsequent years unless a more recent rule exists.')
    points_possible = models.DecimalField(max_digits=8, decimal_places=2, default=4)
    decimal_places = models.IntegerField(default=2)
    def substitute(self, item_or_aggregate, value):
        calculate_as = value
        display_as = None
        for s in self.substitution_set.filter(apply_to_departments=item_or_aggregate.course_section.department, apply_to_categories=item_or_aggregate.category):
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
    ''' A weight assignment for a category within each course section.
    '''
    category = models.ForeignKey('Category')
    weight = models.DecimalField(max_digits=5, decimal_places=4, default=1)
    apply_to_departments = models.ManyToManyField('schedule.Department', blank=True, null=True)
    calculation_rule = models.ForeignKey('CalculationRule', related_name='per_course_category_set')

class CalculationRuleCategoryAsCourse(models.Model):
    ''' A category whose average is given the same weight as a course section in a marking period's average
    '''
    category = models.ForeignKey('Category')
    include_departments = models.ManyToManyField('schedule.Department', blank=True, null=True)
    calculation_rule = models.ForeignKey('CalculationRule', related_name='category_as_course_set')
    special_course_section = models.ForeignKey('schedule.CourseSection',
        help_text=''' Grades for this course section will be OVERWRITTEN by the
        category averages! ''')

class CalculationRuleSubstitution(models.Model):
    operator = models.CharField(max_length=2, choices=OPERATOR_CHOICES)
    match_value = models.DecimalField(max_digits=8, decimal_places=2,
        help_text="Use only (0..1) unless category has fixed points possible.")
    display_as = models.CharField(max_length=16, blank=True, null=True)
    calculate_as = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    flag_visually = models.BooleanField(default=False)
    apply_to_departments = models.ManyToManyField('schedule.Department', blank=True, null=True)
    apply_to_categories = models.ManyToManyField('Category', blank=True, null=True)
    calculation_rule = models.ForeignKey('CalculationRule', related_name='substitution_set')
    def applies_to(self, value):
        # TODO: Compare normalized values?
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
    def as_filter(self, field):
        # TODO: Compare normalized values?
        if self.operator == '>':
            return {u'{}__gt'.format(field): self.match_value}
        if self.operator == '>='.format(field):
            return {u'{}__gte'.format(field): self.match_value}
        if self.operator == '<='.format(field):
            return {u'{}__lte'.format(field): self.match_value}
        if self.operator == '<'.format(field):
            return {u'{}__lt'.format(field): self.match_value}
        if self.operator == '!='.format(field):
            return {u'{}__ne'.format(field): self.match_value}
        if self.operator == '=='.format(field):
            return {u'{}__exact'.format(field): self.match_value}
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
    date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    marking_period = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    category = models.ForeignKey('Category')
    points_possible = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    assignment_type = models.ForeignKey('AssignmentType', blank=True, null=True)
    benchmark = models.ForeignKey('benchmarks.Benchmark', blank=True, null=True, verbose_name='standard')
    @property
    def benchmark_description(self): return self.benchmark.name
    multiplier = models.DecimalField(max_digits=8, decimal_places=2, default=1) # not used yet
    course_section = models.ForeignKey('schedule.CourseSection')
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
    letter_grade = models.CharField(max_length=3, blank=True, null=True, help_text="Overrides numerical mark.")

    # This controls how individual Marks with letter grades are used in averages
    letter_grade_behavior = {
        # dict key is letter grade
        # dict value is tuple of *normalized* value for calculations and
        # whether to dominate any average, e.g. an I on one Mark makes any
        # average that includes it also I.
        "I": (None, True),
        "P": (1, False),
        "F": (0, False),
        # Should A be 90 or 100? A-D aren't used in calculations yet, so just omit them.
        "HP": (1, False),
        "LP": (1, False),
        "M": (0, False),
        # Baltimore
        "MI": (0, False),
        "INC": (0, False),
        "SUB": (None, False),
        "EXC": (None, False),
    }

    class Meta:
        unique_together = ('item', 'demonstration', 'student',)

    def save(self, *args, **kwargs):
        if self.mark is not None and self.item.points_possible is not None:
            # ideally, store a value between 0 and 1, but that only happens if 0 <= self.mark <= self.item.points_possible
            # in practice, people set marks that far exceed points_possible
            self.normalized_mark = float(self.mark) / float(self.item.points_possible)
        super(Mark, self).save(*args, **kwargs)

        # For Categories that allow multiple Demonstrations, store the aggregate
        # mark (attribute) in the Mark (model) that's linked to an Item but not
        # to any Demonstration.
        # This way, reports can be run using `demonstration=None` as a filter
        # to include only one mark per Student per Assignment.
        if self.demonstration is not None and \
        self.item.category.allow_multiple_demonstrations:
            Method = self.item.category.aggregation_method
            aggregated_mark = self.item.mark_set.filter(
                student=self.student
            ).exclude(
                demonstration=None
            ).aggregate(Method('mark')).popitem()[1]
            aggregated_model, created = benchmark_get_create_or_flush(
                Mark, student=self.student, item=self.item, demonstration=None
            )
            aggregated_model.mark = aggregated_mark
            aggregated_model.save()


    def clean(self):
        from django.core.exceptions import ValidationError
        if self.item.category.fixed_granularity and self.mark and self.mark % self.item.category.fixed_granularity != 0:
            raise ValidationError('Mark does not conform to fixed granularity of {}.'.format(self.item.category.fixed_granularity))
    
    def set_grade(self, grade): # in the tradition of Grades.grade
        if grade is None:
            self.mark = self.letter_grade = None
            return
        try:
            self.mark = Decimal(grade)
            self.letter_grade = None
        except InvalidOperation:
            self.letter_grade = grade.upper().strip()
            try:
                if self.item.points_possible is None:
                    raise Exception("Cannot assign a letter grade to a mark whose item does not have a points possible value.")
                self.mark = self.letter_grade_behavior[self.letter_grade][0]
                if self.mark is not None:
                    # numerical equivalents for letter grade are given as normalized values
                    self.mark *= self.item.points_possible
            except KeyError:
                self.mark = None

    def get_grade(self):
        if self.letter_grade is not None:
            return self.letter_grade
        else:
            return self.mark

    def __unicode__(self):
        return unicode(self.mark) + u' - ' + unicode(self.student) + u'; ' + unicode(self.item)
    
class Aggregate(models.Model):
    name = models.CharField(max_length=255)
    manual_mark = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    cached_value = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    cached_substitution = models.CharField(max_length=16, blank=True, null=True)
    student = models.ForeignKey('sis.Student', blank=True, null=True)
    course_section = models.ForeignKey('schedule.CourseSection', blank=True, null=True)
    category = models.ForeignKey('Category', blank=True, null=True)
    marking_period = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    points_possible = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    class Meta:
        unique_together = ('student', 'course_section', 'category', 'marking_period')

    def __getattribute__(self, name):
        ''' Sometimes people use the gradebook for one marking period, but
        something else for another. This is a fairly awful way to display the
        correct course section average in those circumstances. Eventually, we will stop
        calculating course section averages altogether and leave that work to
        ecwsp.grades. '''
        get_ = lambda x: super(Aggregate, self).__getattribute__(x)
        if name == 'cached_value' and \
            get_('cached_value') is None and \
            get_('category_id') is None and \
            get_('course_section_id') is not None and \
            get_('marking_period_id') is not None and \
            get_('student_id') is not None:
            try:
                grade = Grade.objects.get(
                    marking_period_id=get_('marking_period_id'),
                    course_section_id=get_('course_section_id'),
                    student_id=get_('student_id'))
                return grade.grade
            except Grade.DoesNotExist:
                pass
        return super(Aggregate, self).__getattribute__(name)

    def _really_get(self, name):
        ''' Bypass awful __getattribute__ hack '''
        return super(Aggregate, self).__getattribute__(name)

    @property
    def calculation_rule(self):
        ''' Find the CalculationRule that applies to this Aggregate '''
        if self.marking_period is not None:
            return benchmark_find_calculation_rule(self.marking_period.school_year)
        if self.course_section is not None:
            return benchmark_find_calculation_rule(
                self.course_section.marking_period.all()[0].school_year)
        # implicit return None

    @property
    def mark_set(self):
        ''' All the marks needed to calculate this aggregate '''
        item_fields = ('course_section', 'category', 'marking_period')
        criteria = {'student_id': self.student.pk}
        for field in item_fields:
            field += '_id'
            criterium = getattr(self, field)
            if criterium is not None:
                criteria['item__' + field] = criterium
        return Mark.objects.filter(**criteria).exclude(mark=None)

    def mark_values_list(self, normalize=False):
        ''' A list of tuples of (mark, display_as, points_possible) for all the marks
        needed to calculate this aggregate '''
        rule = self.calculation_rule
        if self.category is not None and self.category.allow_multiple_demonstrations:
            if normalize:
                mark_list = self.mark_set.values('item')\
                        .annotate(self.category.aggregation_method('normalized_mark'))\
                        .values_list('normalized_mark__max')
            else:
                mark_list = self.mark_set.values('item')\
                        .annotate(self.category.aggregation_method('mark'))\
                        .values_list('mark__max', 'item__points_possible')
        else:
            if normalize:
                mark_list = self.mark_set.values_list('normalized_mark')
            else:
                mark_list = self.mark_set.values_list('mark', 'item__points_possible')
        if normalize:
            # TODO: handle substitutions
            return [(x[0], 'TODO!', 1) for x in mark_list]
        else:
            final_list = []
            for mark, points_possible in mark_list:
                calculate_as, display_as = rule.substitute(self, mark)
                final_list.append((calculate_as, display_as, points_possible))
            return final_list

    def depends_on(self):
        ''' Returns all Aggregates, in the form of [(Aggregate, created, weight),], immediately required to calculate
        this Aggregate. Not recursive; multiple levels of dependency are NOT considered. '''
        aggregate_tuples = []
        ours = [self.student_id, self.course_section_id,
                self.category_id, self.marking_period_id]
        ours = [x is not None for x in ours]
        if ours == [True, True, True, True]:
            ''' As specific as it gets. Average for one category
            in one course section during one marking period. '''
            return aggregate_tuples
        if ours == [True, True, True, False]:
            ''' Average for one category across the entire duration of the course section. ''' 
            # Not currently used? Gets created by gradebook_recalculate_on_item_change()
            marking_periods = self.course_section.marking_period.all()
            for marking_period in marking_periods:
                aggregate_tuples.append(benchmark_get_create_or_flush(Aggregate, student_id=self.student_id,
                    course_section_id=self.course_section_id, category_id=self.category_id, marking_period_id=marking_period.pk) + (marking_period.weight,))
            return aggregate_tuples
        if ours == [True, True, False, True]:
            ''' Course section grade for one marking period. '''
            rule = self.calculation_rule
            per_course_categories = rule.per_course_category_set.filter(apply_to_departments=self.course_section.department)
            for per_course_category in per_course_categories:
                aggregate_tuples.append(benchmark_get_create_or_flush(Aggregate, student_id=self.student_id,
                    course_section_id=self.course_section_id, category_id=per_course_category.category_id,
                    marking_period_id=self.marking_period_id) + (per_course_category.weight,))
            return aggregate_tuples
        if ours == [True, True, False, False]:
            ''' Overall course section grade, for the entire duration of the course section. '''
            marking_periods = self.course_section.marking_period.all()
            for marking_period in marking_periods:
                aggregate_tuples.append(benchmark_get_create_or_flush(Aggregate, student_id=self.student_id,
                    course_section_id=self.course_section_id, category_id=None, marking_period_id=marking_period.pk) + (marking_period.weight,))
            return aggregate_tuples
        if ours == [True, False, True, True]:
            ''' Average of a category across all course sections for one marking period.
            Some schools count it in GPAs as if it were a course section. '''
            rule = self.calculation_rule
            departments = rule.category_as_course_set.get(category_id=self.category_id).include_departments.all()
            course_sections = self.student.coursesection_set.filter(marking_period=self.marking_period_id,
                course__department__in=departments, course__graded=True, course__course_type__award_credits=True)
            for course_section in course_sections:
                weight = Decimal(course_section.credits) / course_section.marking_period.count()
                aggregate_tuples.append(benchmark_get_create_or_flush(Aggregate, student_id=self.student_id,
                    course_section_id=course_section.pk, category_id=self.category_id, marking_period_id=self.marking_period_id) + (weight,))
            return aggregate_tuples
        raise Exception("Aggregate type unrecognized.")

    def calculate(self, recalculate_all=False):
        numerator = denominator = Decimal(0)
        aggregate_tuples = self.depends_on()
        self.cached_substitution = None
        if not len(aggregate_tuples):
            # Base case: I depend on no Aggregate; calculate from Marks
            self.cached_value, self.cached_substitution = self.mean()
        else:
            for aggregate, created, weight in aggregate_tuples:
                # I depend on other Aggregates
                if created or recalculate_all:
                    aggregate.calculate(recalculate_all)
                if aggregate.cached_value is not None:
                    numerator += weight * aggregate.cached_value
                    denominator += weight
                    if aggregate.cached_substitution is not None:
                        # Allow substitutions to bubble up,
                        # e.g. INC on one Item yields INC on the whole Category and CourseSection
                        self.cached_substitution = aggregate.cached_substitution
            if denominator:
                self.cached_value = numerator / denominator
            else:
                self.cached_value = None
        self.save()

    def _e_pluribus_unum(self, plures):
        ''' Return one from many (display_as substitutions), provided the many have only one unique value
        after excluding None and the empty string '''
        plures = set(plures).difference(set((None, '')))
        if len(plures) == 1:
            unus = plures.pop()
        elif len(plures) == 0:
            unus = None
        else:
            raise Exception('Contradictory display_as substitutions for Aggregate {}: {}'.format(self.pk, plures))
        return unus

    def _fallback_points_possible(self):
        if self.points_possible is not None:
            return self.points_possible
        if self.category is not None and self.category.fixed_points_possible is not None:
            return self.category.fixed_points_possible
        rule = self.calculation_rule
        if rule is not None and rule.points_possible is not None:
            return rule.points_possible

    def max(self):
        mark_values_list = self.mark_values_list(normalize=True)
        if not len(mark_values_list):
            return None, None
        mark, display_as, item_points_possible = zip(*mark_values_list)
        display_as = self._e_pluribus_unum(display_as)
        if len(mark):
            return (Decimal(max(mark)) * self._fallback_points_possible(), display_as)
        else:
            return None, display_as

    def min(self):
        mark_values_list = self.mark_values_list(normalize=True)
        if not len(mark_values_list):
            return None, None
        mark, display_as, item_points_possible = zip(*mark_values_list)
        display_as = self._e_pluribus_unum(display_as)
        if len(mark):
            return Decimal(min(mark)) * self._fallback_points_possible()
        else:
            return None, display_as

    def mean(self, normalize=False):
        mark_values_list = self.mark_values_list(normalize)
        if not len(mark_values_list):
            return None, None
        mark, display_as, item_points_possible = zip(*mark_values_list)
        display_as = self._e_pluribus_unum(display_as)
        total_points_possible = sum(item_points_possible)
        if total_points_possible:
            return Decimal(sum(mark) / total_points_possible) * self._fallback_points_possible(), display_as
        else:
            return None, display_as

    def _copy_to_grade(self):
        # Bypass awful __getattribute__ hack. If we're here, we're the
        # authority, and grades.Grade must defer to us.
        this_cached_value = self._really_get('cached_value')
        this_cached_substitution = self._really_get('cached_substitution')
        # temporary(?) integration with the rest of sword
        g, g_created = Grade.objects.get_or_create(student=self.student,
            course_section=self.course_section,
            marking_period=self.marking_period,
            override_final=False)
        # set the letter grade if it exists
        if this_cached_substitution is not None:
            # FIDDLESTICKS... INC does not fit in the column
            letter_grade_max_length = Grade._meta.get_field_by_name('letter_grade')[0].max_length
            g.letter_grade = this_cached_substitution[:letter_grade_max_length]
        else:
            g.letter_grade = None
        # always set the numeric grade
        grade_max_value = Grade._meta.get_field_by_name('grade')[0]
        # whee...
        grade_max_value = 10 ** (grade_max_value.max_digits - grade_max_value.decimal_places) - 10 ** (-1 * grade_max_value.decimal_places)
        if this_cached_value > grade_max_value:
            # people abuse points_possible (set marks way above it),
            # either to give out extra credit or because they are just screwing around.
            # don't attempt to set a Grade larger than the maximum permissable value
            g.grade = grade_max_value
        else:
            g.grade = this_cached_value
        g.save()
        return g, g_created

    def _copy_to_special_course_section(self):
        special_course_section = self.calculation_rule.category_as_course_set.get(
            category_id=self.category_id).special_course_section
        # make sure our MarkingPeriod is assigned to the CourseSection
        self.marking_period.coursesection_set.add(special_course_section)
        # make sure our Student is enrolled in the CourseSection
        special_course_section.courseenrollment_set.get_or_create(user=self.student)
        # copy our average to ecwsp.grades
        g, g_created = Grade.objects.get_or_create(student=self.student,
            course_section=special_course_section, marking_period=self.marking_period,
            override_final=False)
        g.set_grade(self.cached_value)
        g.save()
        return g, g_created

    def save(self, *args, **kwargs):
        ours = [self.student_id, self.course_section_id,
                self.category_id, self.marking_period_id]
        ours = [x is not None for x in ours]
        if ours == [True, True, False, True]:
            ''' CourseSection grade for one marking period. '''
            if not CalculationRuleCategoryAsCourse.objects.filter(
                special_course_section=self.course_section
            ).exists():
                # Don't overwite the category-as-course grades!
                self._copy_to_grade()
        if ours == [True, False, True, True]:
            ''' Average of a category across all course sections for one marking period.
            Some schools count it in GPAs as if it were a course section. '''
            self._copy_to_special_course_section()
        super(Aggregate, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name # not useful

class AggregateTask(models.Model):
    ''' A Celery task in the process of recalculating an Aggregate '''
    aggregate = models.ForeignKey('Aggregate')
    task_id = models.CharField(max_length=36)
    timestamp = models.DateTimeField(default=datetime.now)
    class Meta:
        unique_together = ('aggregate', 'task_id')
