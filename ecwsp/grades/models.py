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

    @staticmethod
    def get_enrollment(student, course_section):
        return student.courseenrollment_set.get(
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

    @classmethod
    def set_marking_period_student_course_grade(cls, marking_period, student,
                                                course_section, grade):
        """ Set a grade based looking up the enrollment object
        Returns grade object or None """
        enrollment = cls.get_enrollment(student, course_section)
        return cls.set_marking_period_grade(marking_period, enrollment, grade)

    @staticmethod
    def set_marking_period_grade(marking_period, enrollment, grade):
        """ Set a grade from an enrollment and marking period
        A grade of None will delete the grade object making it not used in
        any calculations.
        Create grade object when it doesn't exist and is not None
        Delete grade object when grade is set to None
        Returns grade object or None
        """
        search_kwargs = {
            'enrollment': enrollment,
            'marking_period': marking_period,
        }
        if grade is None:
            try:
                grade_obj = Grade.objects.get(**search_kwargs)
                grade_obj.delete()
            except Grade.DoesNotExist:
                pass
        else:
            grade_obj, created = Grade.objects.get_or_create(**search_kwargs)
            grade_obj.set_grade(grade)
            grade_obj.save()
            return grade_obj

    @staticmethod
    def get_course_grade(enrollment,
                         date=None,
                         rounding=None,
                         marking_periods=None,
                         letter=False,
                         letter_and_number=False):
        """Get course final grade by calulating it or from override

        Args:
            enrollment: CourseEnrollment object
            date: Date of report - used to exclude grades that haven't happened
            rounding: Explicit rounding - defaults to global config
            marking_periods: Filter grades by these
            letter: Return letter grade from scale
            letter_and_number: Return string like 87.65 (B+)
        """
        if rounding is None:
            rounding = config.GRADE_ROUNDING_DECIMAL
        grades = enrollment.grade_set.all()
        if date is not None:
            grades = grades.filter(marking_period__end_date__lte=date)
        if marking_periods is not None:
            grades = grades.filter(marking_period__in=marking_periods)
        grades = grades.values_list(
            'grade',
            'marking_period',
            'marking_period__weight',
            'enrollment__finalgrade__grade',
        )
        if not grades:
            return None
        np_grades = np.array(grades, dtype=np.dtype(float))
        np_grade_values = np_grades[:, 0]
        np_grade_values_mask = ~np.isnan(np_grade_values)
        np_mp = np_grades[:, 1]
        np_mp_weights = np_grades[:, 2]
        np_final_grades = np_grades[:, 3]
        # If marking periods are selected - don't return final override
        if not marking_periods and array_contains_anything(np_final_grades):
            average = np_final_grades[0]
        else:
            average = np.average(
                np_grade_values[np_grade_values_mask],
                weights=np_mp_weights[np_grade_values_mask])
        result = grade = np.round(
            average + 0.00000000000001,  # Work around floating point rounding
            decimals=rounding)
        if letter is True:
            result = letter_grade = GradeScaleRule.grade_to_scale(
                grade, np_mp[0], letter=True)
            if letter_and_number is True:
                result = '{} ({})'.format(grade, letter_grade)
        return result

    @staticmethod
    def get_marking_period_average(student, marking_period):
        student.grade



class FinalGrade(CommonGrade):
    enrollment = models.ForeignKey('schedule.CourseEnrollment', unique=True)

    def set_grade(self, grade):
        self.grade = grade

    @classmethod
    def set_student_course_final_grade(cls, student, course_section, grade):
        """ Set a grade based looking up the enrollment object
        Returns grade object or None """
        enrollment = cls.get_enrollment(student, course_section)
        return cls.set_final_grade(enrollment, grade)

    @classmethod
    def set_final_grade(cls, enrollment, grade):
        """ Set a grade from an enrollment
        A grade of None will delete the grade object making it not used in
        any calculations.
        """
        search_kwargs = {'enrollment': enrollment}
        if grade is None:
            try:
                grade_obj = cls.objects.get(**search_kwargs)
                grade_obj.delete()
            except Grade.DoesNotExist:
                pass
        else:
            grade_obj, created = cls.objects.get_or_create(**search_kwargs)
            grade_obj.set_grade(grade)
            grade_obj.save()
            return grade_obj
