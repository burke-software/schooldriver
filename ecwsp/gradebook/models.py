from django.db import models
from django.db.models import Q, Max
from django.conf import settings
from ecwsp.sis.models import SchoolYear
from .exceptions import WeightContainsNone
from decimal import Decimal
import numpy as np


class WeightField(models.DecimalField):
    def __init__(self, separator=",", *args, **kwargs):
        kwargs['max_digits'] = 5
        kwargs['decimal_places'] = 4
        kwargs['default'] = 1
        super(WeightField, self).__init__(*args, **kwargs)


class GradeField(models.DecimalField):
    def __init__(self, separator=",", *args, **kwargs):
        kwargs['max_digits'] = 8
        kwargs['decimal_places'] = 2
        kwargs['blank'] = True
        kwargs['null'] = True
        super(GradeField, self).__init__(*args, **kwargs)


OPERATOR_CHOICES = (
    (u'>', u'Greater than'),
    (u'>=', u'Greater than or equal to'),
    (u'<=', u'Less than or equal to'),
    (u'<', u'Less than'),
    (u'!=', u'Not equal to'),
    (u'==', u'Equal to')
)
NP_OPERATOR_MAP = {
    '>': np.greater,
    '>=': np.greater_equal,
    '<=':  np.less_equal,
    '<': np.less,
    '!=': np.not_equal,
    '==': np.equal,
}
AGGREGATE_METHODS = (
    (u'Avg', u'Average'),
    (u'Count', u'Count'),
    (u'Max', u'Maximum'),
    (u'Min', u'Minimum'),
    (u'StdDev', u'Standard deviation'),
    (u'Sum', u'Sum'),
    (u'Variance', u'Variance')
)


# Meta data about grade calculations ##############################

class CalculationRule(models.Model):
    ''' A per-year GPA calculation rule.
    It should also be applied to future years unless a more current rule exists.
    Potential calculation components:
        career, year, marking period, course section
    '''
    first_year_effective = models.ForeignKey(
        'sis.SchoolYear',
        unique=True,
        related_name="gradebook_calculationrule_set",
        help_text='Rule also applies to subsequent years.')
    points_possible = GradeField(
        default=100,
        help_text=(
            "A teachergradebook is out of this many points. "
            "Or the max possible points a student can earn. "
            "Common examples are 100 or 4.0."),
        blank=False, null=False)
    decimal_places = models.IntegerField(default=2)

    @staticmethod
    def find_calculation_rule(school_year):
        rules = CalculationRule.objects.filter(
            first_year_effective__start_date__lte=school_year.start_date
        ).order_by('-first_year_effective__start_date')
        return rules.first()

    @staticmethod
    def find_active_calculation_rule():
        """ Find the active calc rule
        Potential target for raw sql optimization
        """
        school_year = SchoolYear.objects.filter(active_year=True).first()
        return CalculationRule.find_calculation_rule(school_year)


class AssignmentCategory(models.Model):
    """ Unlike type this must be highly controlled by a school admin.
    It's used mainly for benchmark driven grades.
    """
    name = models.CharField(max_length=255)
    allow_multiple_demonstrations = models.BooleanField(default=False)
    demonstration_aggregation_method = models.CharField(
        max_length=16, choices=AGGREGATE_METHODS, blank=True, null=True)
    display_in_gradebook = models.BooleanField(default=True)
    fixed_points_possible = GradeField()
    fixed_granularity = GradeField()
    display_order = models.IntegerField(unique=True, blank=True, null=True)
    display_scale = GradeField()
    display_symbol = models.CharField(max_length=7, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['display_order']


class CalculationRuleSubstitution(models.Model):
    operator = models.CharField(max_length=2, choices=OPERATOR_CHOICES)
    match_value = GradeField(
        blank=False, null=False,
        help_text="Use only (0..1) unless category has fixed points possible.")
    display_as = models.CharField(max_length=16, blank=True, null=True)
    calculate_as = GradeField()
    flag_visually = models.BooleanField(default=False)
    apply_to_departments = models.ManyToManyField(
        'schedule.Department', blank=True, null=True, related_name="+")
    apply_to_categories = models.ManyToManyField(
        AssignmentCategory, blank=True, null=True)
    calculation_rule = models.ForeignKey(
        CalculationRule, related_name='substitution_set')

    def np_check_if_matches(self, np_array):
        """ Check a numpy array to see if it matchse the sub criteria
        Assumes that the numpy array contains only marks that meet
        the apply_to criteria of this substituion rule
        Returns False when sub rules doesn't match """
        desired_np_function = NP_OPERATOR_MAP[self.operator]
        if any(desired_np_function(np_array, self.match_value)):
            return True
        return False


class CalculationRulePerCourseCategory(models.Model):
    ''' A weight assignment for a category within each course section.
    '''
    category = models.ForeignKey(AssignmentCategory)
    weight = WeightField()
    apply_to_departments = models.ManyToManyField(
        'schedule.Department', blank=True, null=True,
        related_name='gradebook_calculationrulepercoursecategory_set')
    calculation_rule = models.ForeignKey(
        CalculationRule, related_name='per_course_category_set')


# Assignment and Mark Data Models ################################

class AssignmentType(models.Model):
    """ A teacher selectable assignment type
    Might be enforced as a school wide settings or teachers can create their
    own as needed.
    """
    name = models.CharField(max_length=255)
    weight = WeightField()
    is_default = models.BooleanField(default=False)
    teacher = models.ForeignKey('sis.Faculty', blank=True, null=True)

    def __unicode__(self):
        return self


class Assignment(models.Model):
    """ An assignment that a student could have a grade for """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(
        blank=True, null=True)#, validators=settings.DATE_VALIDATORS)
    marking_period = models.ForeignKey(
        'schedule.MarkingPeriod', blank=True, null=True)
    category = models.ForeignKey(AssignmentCategory, blank=True, null=True)
    points_possible = GradeField()
    assignment_type = models.ForeignKey(AssignmentType, blank=True, null=True)
    benchmark = models.ForeignKey(
        'benchmarks.Benchmark', blank=True, null=True, verbose_name='standard')
    course_section = models.ForeignKey('schedule.CourseSection')

    def __unicode__(self):
        return self.name


class Demonstration(models.Model):
    """ In a benchmark driven system a student can "demostrate" they understand
    some assignment multiple times.
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    assignment = models.ForeignKey(Assignment)

    def __unicode__(self):
        return self.name + u' - ' + unicode(self.item)


def array_contains_anything(np_array):
    """ Return true if numpy array contains any values above 0
    Does not work with negative values """
    if np.nansum(np_array) > 0:
        return True
    return False


def grade_weighted_average(
    marks_category,
    marks_category_weight,
    marks_percent,
    marks_possible,
    marks_assignment=None,
    marks_assignment_weight=None,
):
    if array_contains_anything(marks_category_weight):
        if np.isnan(np.sum(marks_category_weight)):
            raise WeightContainsNone()
        all_categories, first_indexes = np.unique(
            marks_category, return_index=True)
        all_categories_weights = marks_category_weight[first_indexes]
        cat_totals = []
        for category in all_categories:
            cat_indexes = np.where(marks_category == category)
            if marks_assignment is not None and any(marks_assignment):
                assign_total = grade_weighted_average(
                    marks_assignment[cat_indexes],
                    marks_assignment_weight[cat_indexes],
                    marks_percent[cat_indexes],
                    marks_possible[cat_indexes],
                )
                cat_totals += [assign_total]
            else:
                cat_percent = marks_percent[cat_indexes]
                cat_weights = marks_possible[cat_indexes]
                cat_totals += [np.average(cat_percent, weights=cat_weights)]
    else:  # Easy then
        if marks_assignment is not None and any(marks_assignment):
            assign_total = grade_weighted_average(
                marks_assignment,
                marks_assignment_weight,
                marks_percent,
                marks_possible,
            )
            return assign_total
        cat_totals = marks_percent
        all_categories_weights = marks_possible
    return np.average(cat_totals, weights=all_categories_weights)


class Mark(models.Model):
    """ A Mark (aka grade) earned by a student in a particular Assignment """
    assignment = models.ForeignKey(Assignment)
    demonstration = models.ForeignKey(Demonstration, blank=True, null=True)
    student = models.ForeignKey(
        'sis.Student', related_name="gradebook_mark_set")
    mark = GradeField()
    normalized_mark = models.FloatField(blank=True, null=True)
    letter_grade = models.CharField(
        max_length=3, blank=True, null=True,
        help_text="Overrides numerical mark.")

    class Meta:
        unique_together = ('assignment', 'demonstration', 'student',)

    def calculate_student_course_grade(self):
        student = self.student
        marking_period = self.assignment.marking_period
        course = self.assignment.course_section
        calc_rule = CalculationRule.find_calculation_rule(
            marking_period.school_year)
        grade = course.grade_set.filter(
            marking_period=marking_period,
            student=student,
            course_section=course,
        ).first()

        # Holy crap. We need to deal with grades when demonstrations exist
        # and pick the best score for a set of demonstrations. But also
        # select marks that have no demonstrations. We'll use order_by
        # to effectively group by demonstration assignment. But a mark with no
        # demonstration will be it's own group. Then find the max mark in that
        # group. See /docs/specs/gradebook.md for more info.
        # Also see Django docs on order_by.
        # https://docs.djangoproject.com/en/dev/topics/db/aggregation/#interaction-with-default-ordering-or-order-by
        marks = student.gradebook_mark_set.filter(
            Q(assignment__marking_period=marking_period),
            Q(assignment__category__calculationrulepercoursecategory__apply_to_departments=course.course.department) |
            Q(assignment__category__calculationrulepercoursecategory__apply_to_departments=None),
        ).exclude(
            mark=None,
        ).order_by(  # Here is the magic - really this is grouping by
            'assignment'
        ).values_list(
            'assignment__points_possible',
            'assignment__category__calculationrulepercoursecategory',
            'assignment__category__calculationrulepercoursecategory__weight',
            'assignment__assignment_type',
            'assignment__assignment_type__weight',
        ).annotate(mark=Max('mark'))

        if not marks:
            grade.set_grade(None)
            return

        np_marks = np.array(marks, dtype=np.dtype(float))
        marks_possible = np_marks[:, 0]
        marks_category = np_marks[:, 1]
        marks_category_weight = np_marks[:, 2]
        marks_assignment = np_marks[:, 3]
        marks_assignment_weight = np_marks[:, 4]
        marks_mark = np_marks[:, 5]
        marks_percent = marks_mark / marks_possible

        if np.isnan(np.sum(marks_possible)):
            raise WeightContainsNone()

        sub_rules = CalculationRuleSubstitution.objects.filter(
            Q(calculation_rule=calc_rule),
            Q(apply_to_departments=course.course.department) |
            Q(apply_to_departments=None)
        ).distinct()

        total = None
        match_sub_rule = False
        for rule in sub_rules:
            cat_ids = rule.apply_to_categories.values_list('id', flat=True)
            relevant_marks = marks_mark
            match_sub_rule = rule.np_check_if_matches(relevant_marks)
            if match_sub_rule is True:
                match_sub_rule = rule
                total = match_sub_rule.calculate_as
                break

        if match_sub_rule is False or total is None:
            # Check if contains any weights at all
            total = grade_weighted_average(
                marks_category, marks_category_weight, marks_percent,
                marks_possible, marks_assignment, marks_assignment_weight)

            if calc_rule is not None and calc_rule.points_possible > 0:
                total = Decimal(total) * calc_rule.points_possible
            else:  # Assume out of 100 unless specified
                total = Decimal(total) * 100

        if match_sub_rule is False:
            grade.set_grade(total, treat_as_percent=False)
        else:
            grade.set_grade(
                total,
                letter_grade=match_sub_rule.display_as,
                treat_as_percent=False)
        grade.save()

    def save(self, *args, **kwargs):
        super(Mark, self).save(*args, **kwargs)
        self.calculate_student_course_grade()
