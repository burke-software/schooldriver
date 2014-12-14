from django.db import models
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
        blank=True, null=True, validators=settings.DATE_VALIDATORS)
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
    item = models.ForeignKey(Assignment)

    def __unicode__(self):
        return self.name + u' - ' + unicode(self.item)


def array_contains_anything(np_array):
    """ Return true if numpy array contains any values above 0
    Does not work with negative values """
    if np.nansum(np_array) > 0:
        return True
    return False


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
        marks = student.gradebook_mark_set.filter(
            assignment__marking_period=marking_period,
            assignment__category__calculationrulepercoursecategory__apply_to_departments=course.course.department
        ).values_list(
            'mark',
            'assignment__points_possible',
            'assignment__category_id',
            'assignment__category__calculationrulepercoursecategory__weight',
            'assignment__assignment_type',
            'assignment__assignment_type__weight',
        )
        marks_mark = np.array(marks, dtype=np.dtype(float))[:, 0]
        marks_possible = np.array(marks, dtype=np.dtype(float))[:, 1]
        marks_category_weight = np.array(marks, dtype=np.dtype(float))[:, 3]
        marks_assignment_weight = np.array(marks, dtype=np.dtype(float))[:, 5]
        marks_percent = marks_mark / marks_possible
        weights = marks_possible

        # Check if contains any weights at all
        if (calc_rule is not None
                and array_contains_anything(marks_category_weight)):
            weights = weights * marks_category_weight
        if array_contains_anything(marks_assignment_weight):
            weights = weights * marks_assignment_weight
        if np.isnan(np.sum(weights)):
            raise WeightContainsNone()
        total = np.average(marks_percent, weights=weights)
        if calc_rule is not None and calc_rule.points_possible > 0:
            total = Decimal(total) * calc_rule.points_possible / Decimal(100)

        grade.set_grade(total)
        grade.save()

    def save(self, *args, **kwargs):
        super(Mark, self).save(*args, **kwargs)
        self.calculate_student_course_grade()
