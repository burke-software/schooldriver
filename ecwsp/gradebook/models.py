from django.db import models
from django.conf import settings


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
        from django.db.models import Sum
        student = self.student
        marking_period = self.assignment.marking_period
        course = self.assignment.course_section
        grade = course.grade_set.filter(
            marking_period=marking_period,
            student=student,
            course_section=course,
        ).first()
        marks = student.gradebook_mark_set.filter(
            assignment__marking_period=marking_period
        ).aggregate(Sum('mark'))['mark__sum']
        possible = Assignment.objects.filter(mark__student=student).aggregate(
            Sum('points_possible'))['points_possible__sum']
        total = marks/possible
        grade.set_grade(total)
        grade.save()

    def save(self, *args, **kwargs):
        super(Mark, self).save(*args, **kwargs)
        self.calculate_student_course_grade()

