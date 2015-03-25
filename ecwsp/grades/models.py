from django.core.validators import MaxLengthValidator
from django.db import models
from ecwsp.sis.models import GradeScaleRule
from ecwsp.sis.constants import GradeField
from constance import config


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


class LetterGrade(models.Model):
    """ Valid letter grade options """
    letter = models.CharField(max_length=50)
    is_passing = models.BooleanField(
        default=True,
        help_text="True means this counts as a Passing or 100% grade.")
    affects_grade = models.BooleanField(
        default=True,
        help_text="True means this has an affect on grade calculations")

    def __unicode__(self):
        return self.letter


class CommonGrade(models.Model):
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    grade = GradeField()
    comment = models.CharField(
        max_length=500, blank=True, validators=[grade_comment_length_validator])
    letter_grade = models.ForeignKey(
        'grades.LetterGrade', blank=True, null=True)

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

    def set_grade(self, grade, letter_grade=None):
        """ Set grade value of this grade object
        Args:
            grade: Grade value to set.
            letter_grade: String of valid LetterGrade, int, or LetterGrade
        """
        self.grade = grade
        if type(letter_grade) in [str, unicode]:
            self.letter_grade = LetterGrade.objects.get(letter=letter_grade)
        elif type(letter_grade) in [int, LetterGrade]:
            self.letter_grade = letter_grade
        elif letter_grade is not None:
            raise ValueError(
                "letter_grade should be string, int, or LetterGrade")
        else:
            self.letter_grade = None

    def get_grade(self, letter=False, letter_and_number=False):
        """ Get the grade, typically for display (not calculations)
        If the grade object contains a letter grade - this will be returned
        Otherwise the grade will.
        Args:
            letter: Convert numeric grade to letter
            letter_and_number: Return both numeric and letter grade
        """
        grade = self.grade
        if letter is True or letter_and_number is True:
            try:
                result = self.grade_to_scale(letter=True)
            except GradeScaleRule.DoesNotExist:
                return "No Grade Scale"
            if letter_and_number is True:
                result = '{} ({})'.format(grade, result)
            return result
        if self.letter_grade is not None:
            return self.letter_grade.letter
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
    def set_marking_period_student_course_grade(
        cls, marking_period, student, course_section, grade, letter_grade=None
    ):
        """ Set a grade based looking up the enrollment object
        Returns grade object or None """
        enrollment = cls.get_enrollment(student, course_section)
        return cls.set_marking_period_grade(
            marking_period, enrollment, grade, letter_grade=letter_grade)

    @staticmethod
    def set_marking_period_grade(
        marking_period, enrollment, grade, letter_grade=None
    ):
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
        if grade is None and letter_grade is None:
            try:
                grade_obj = Grade.objects.get(**search_kwargs)
                grade_obj.delete()
            except Grade.DoesNotExist:
                pass
            return
        grade_obj, created = Grade.objects.get_or_create(**search_kwargs)
        grade_obj.set_grade(grade, letter_grade=letter_grade)
        grade_obj.save()
        return grade_obj


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
