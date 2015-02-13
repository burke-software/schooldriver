from django.core.validators import MaxLengthValidator
from django.db import models
from ecwsp.sis.models import GradeScaleRule
from ecwsp.sis.constants import GradeField
from ecwsp.sis.num_utils import array_contains_anything
from constance import config
import numpy as np


class GradeComment(models.Model):
    """ Optional pre defined comment
    Used when free thought on report cards is discouraged
    """
    # Allow users to set the id, instead of auto inc
    id = models.IntegerField(primary_key=True)
    comment = models.CharField(max_length=500)

    def __unicode__(self):
        return unicode(self.id) + ": " + unicode(self.comment)

    class Meta:
        ordering = ('id',)


def grade_comment_length_validator(value):
    max_length = config.GRADE_COMMEND_LENGTH_LIMIT
    validator = MaxLengthValidator(max_length)
    return validator(value)


class LetterGradeChoices(models.Model):
    """ Valid letter grade options """
    letter = models.CharField(max_length=50)

    def __unicode__(self):
        return self.letter


class CommonGrade(models.Model):
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    grade = GradeField()
    comment = models.CharField(
        max_length=500, blank=True, validators=[grade_comment_length_validator])
    letter_grade = models.ForeignKey(LetterGradeChoices, blank=True, null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return str(self.grade)

    def set_enrollment(self, student, course_section):
        self.enrollment = student.courseenrollment_set.get(
            course_section=course_section)


class Grade(CommonGrade):
    enrollment = models.ForeignKey('schedule.CourseEnrollment')
    marking_period = models.ForeignKey(
        'schedule.MarkingPeriod', blank=True, null=True)

    class Meta:
        unique_together = (("enrollment", "marking_period"),)
        permissions = (
            ("change_own_grade", "Change grades for own class"),
            ('change_own_final_grade', 'Change final YTD grades for own class'),
        )

    @property
    def student(self):
        return self.enrollment.user

    @property
    def student_id(self):
        return self.student.id

    @property
    def course_section(self):
        return self.enrollment.course_section

    @property
    def course_section_id(self):
        return self.course_section.id

    def set_grade(self, grade):
        self.grade = grade

    def get_grade(self, letter=False, letter_and_number=False):
        grade = self.grade
        if letter is True or letter_and_number is True:
            try:
                result = self.grade_to_scale(letter=True)
            except GradeScaleRule.DoesNotExist:
                return "No Grade Scale"
            if letter_and_number is True:
                result = '{} ({})'.format(grade, result)
            return result
        return grade

    def grade_to_scale(self, letter):
        """ letter - True for letter grade, false for numeric (ex: 4.0 scale)
        """
        rule = GradeScaleRule.objects.filter(
            grade_scale__schoolyear__markingperiod=self.marking_period_id,
            min_grade__lte=self.grade,
            max_grade__gte=self.grade,
        ).first()
        if letter is True:
            return rule.letter_grade
        return rule.numeric_scale

    @staticmethod
    def set_grade_from_marking_period_student(marking_period, student, grade):
        pass
        #try:
        #    grade Grade.objects.get()

    @staticmethod
    def get_course_grade(enrollment, date=None, rounding=None):
        if rounding is None:
            rounding = config.GRADE_ROUNDING_DECIMAL
        grades = enrollment.grade_set.all()
        if date is not None:
            grades = grades.filter(marking_period__end_date__lte=date)
        grades = grades.values_list(
            'grade',
            'marking_period__weight',
            'enrollment__finalgrade__grade',
        )
        np_grades = np.array(grades, dtype=np.dtype(float))
        np_grade_values = np_grades[:, 0]
        np_mp_weights = np_grades[:, 1]
        np_final_grades = np_grades[:, 2]
        if array_contains_anything(np_final_grades):
            average = np_final_grades[0]
        else:
            average = np.average(np_grade_values, weights=np_mp_weights)
        return np.round(average, decimals=rounding)


class FinalGrade(CommonGrade):
    enrollment = models.ForeignKey('schedule.CourseEnrollment', unique=True)

    def set_grade(self, grade):
        self.grade = grade
