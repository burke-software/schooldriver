from django.core.exceptions import ValidationError
from django.db import models, connection
from django.db.models import Count, Sum
from django.conf import settings
from django.core.validators import MaxLengthValidator
from ecwsp.sis.models import Student, GradeScaleRule
from ecwsp.sis.helper_functions import round_as_decimal
from ecwsp.administration.models import Configuration
from django_cached_field import CachedDecimalField

import decimal
from decimal import Decimal
import datetime
import ecwsp
import logging


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
    max_length = int(Configuration.get_or_default(
        'Grade comment length limit').value)
    validator = MaxLengthValidator(max_length)
    return validator(value)


class StudentMarkingPeriodGrade(models.Model):
    """ Stores marking period grades for students, only used for cache """
    student = models.ForeignKey('sis.Student')
    marking_period = models.ForeignKey(
        'schedule.MarkingPeriod', blank=True, null=True)
    grade = CachedDecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        verbose_name="MP Average")

    class Meta:
        unique_together = ('student', 'marking_period')

    def get_average(self, rounding=2):
        """ Returns cached average """
        return round_as_decimal(self.grade, rounding)

    def get_scaled_average(self, rounding=2, boost=True):
        """ Convert to scaled grade first, then average
        Burke Software does not endorse this as a precise way to calculate
        averages """
        grade_total = 0.0
        total_credits = 0.0
        grades = self.student.grade_set.filter(
            marking_period=self.marking_period,
            grade__isnull=False,
            course_section__course__course_type__weight__gt=0,
            enrollment__is_active=True,
        )

        for grade in grades:
            grade_value = float(grade.optimized_grade_to_scale(letter=False))
            if grade_value > 0 and boost:
                # only add boost for non-failing grades
                grade_value += float(grade.course_section.course.course_type.boost)
            num_credits = float(grade.course_section.course.credits)
            grade_total += grade_value * num_credits
            total_credits += num_credits
        if total_credits > 0:
            average = grade_total / total_credits
            return round_as_decimal(average, rounding)
        else:
            return None

    @staticmethod
    def build_all_cache():
        """ Create object for each student * possible marking periods """
        for student in Student.objects.all():
            marking_periods = student.courseenrollment_set.values(
                'course_section__marking_period').annotate(
                    Count('course_section__marking_period'))
            for marking_period in marking_periods:
                StudentMarkingPeriodGrade.objects.get_or_create(
                    student=student,
                    marking_period_id=marking_period['course_section__marking_period'])

    def calculate_grade(self):
        cursor = connection.cursor()
        sql_string = """
select sum(grade * credits) / sum(credits * 1.0)
from grades_grade
left join schedule_coursesection on schedule_coursesection.id=grades_grade.course_section_id
left join schedule_course on schedule_coursesection.course_id=schedule_course.id
where marking_period_id=%s and student_id=%s and grade is not null;"""
        cursor.execute(sql_string, (self.marking_period_id, self.student_id))
        result = cursor.fetchone()
        if result:
            return result[0]


class StudentYearGrade(models.Model):
    """ Stores the grade for an entire year, only used for cache """
    student = models.ForeignKey('sis.Student')
    year = models.ForeignKey('sis.SchoolYear')
    grade = CachedDecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Year average")
    credits = CachedDecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'year')

    @staticmethod
    def build_cache_student(student):
        years = student.courseenrollment_set.values(
            'course_section__marking_period__school_year'
            ).annotate(Count('course_section__marking_period__school_year'))
        for year in years:
            if year['course_section__marking_period__school_year']:
                year_grade = StudentYearGrade.objects.get_or_create(
                    student=student,
                    year_id=year['course_section__marking_period__school_year']
                )[0]
                if year_grade.credits_recalculation_needed:
                    year_grade.recalculate_credits()
                if year_grade.grade_recalculation_needed:
                    year_grade.recalculate_grade()

    @staticmethod
    def build_all_cache(*args, **kwargs):
        """ Create object for each student * possible years """
        if 'instance' in kwargs:
            StudentYearGrade.build_cache_student(kwargs['instance'])
        else:
            for student in Student.objects.all():
                StudentYearGrade.build_cache_student(student)

    def calculate_credits(self):
        """ The number of credits a student has earned in 1 year """
        return self.calculate_grade_and_credits()[1]

    def calculate_grade_and_credits(self, date_report=None, prescale=False):
        """ Just recalculate them both at once
        returns (grade, credits)

        if "prescale=True" grades are scaled (i.e. 4.0) before averaged
        """
        total = Decimal(0)
        credits = Decimal(0)
        prescaled_grade = Decimal(0)
        grade_scale = self.year.grade_scale
        for course_enrollment in self.student.courseenrollment_set.filter(
            course_section__marking_period__show_reports=True,
            course_section__marking_period__school_year=self.year,
            course_section__course__credits__isnull=False,
            course_section__course__course_type__weight__gt=0,
            ).distinct():
            grade = course_enrollment.calculate_grade_real(date_report=date_report, ignore_letter=True)
            if grade:
                num_credits = course_enrollment.course_section.course.credits
                if prescale:
                    # scale the grades before averaging them if requested
                    if grade_scale:
                        grade = grade_scale.to_numeric(grade)
                    prescaled_grade += grade * num_credits
                total += grade * num_credits
                credits += num_credits
        if credits > 0:
            grade = total / credits
            if prescale:
                prescaled_grade = prescaled_grade / credits
        else:
            grade = None
        if date_report == None: # If set would indicate this is not for cache!
            self.grade = grade
            self.credits = credits
            self.grade_recalculation_needed = False
            self.credits_recalculation_needed = False
            self.save()

        if prescale:
            return (prescaled_grade, credits)
        else:
            return (grade, credits)

    def calculate_grade(self, date_report=None, prescale=False):
        """ Calculate grade considering MP weights and course credits
        course_enrollment.calculate_real_grade returns a MP weighted result,
        so just have to consider credits
        """
        return self.calculate_grade_and_credits(date_report=date_report, prescale=prescale)[0]

    def get_grade(self, date_report=None, rounding=2, numeric_scale=False,
                  prescale=False, boost=True):
        if numeric_scale == False and (date_report is None or date_report >= datetime.date.today()):
            # Cache will always have the latest grade, so it's fine for
            # today's date and any future date
            return self.grade
        grade = self.calculate_grade(date_report=date_report, prescale=prescale)
        if numeric_scale == True:
            grade_scale = self.year.grade_scale
            if grade_scale and not prescale:
                grade = grade_scale.to_numeric(grade)
            if boost:
                enrollments = self.student.courseenrollment_set.filter(
                    course_section__marking_period__show_reports=True,
                    course_section__marking_period__school_year=self.year,
                    course_section__course__credits__isnull=False,
                    course_section__course__course_type__weight__gt=0,)
                if not grade_scale:
                    boost_sum = enrollments.aggregate(boost_sum=Sum('course_section__course__course_type__boost'))['boost_sum']
                    if not boost_sum:
                        boost_sum = 0.0
                    try:
                        boost_factor = boost_sum / enrollments.count()
                    except ZeroDivisionError:
                        boost_factor = 0.0
                else:
                    boost_sum = 0.0
                    total_credits = 0.0
                    for enrollment in enrollments:
                        course_credits = enrollment.course_section.course.credits
                        course_boost = enrollment.course_section.course.course_type.boost
                        if enrollment.numeric_grade:
                            course_grade = Decimal(enrollment.numeric_grade)
                            total_credits += float(course_credits)
                            if grade_scale.to_numeric(course_grade) > 0:
                                # only add boost to grades that are not failing...
                                boost_sum += float(course_boost*course_credits)

                    try:
                        boost_factor = boost_sum / total_credits
                    except ZeroDivisionError:
                        boost_factor = None
                if enrollments.count() > 0 and boost_factor and grade:
                    grade = float(grade) + float(boost_factor)
        if rounding:
            grade = round_as_decimal(grade, rounding)
        return grade

#signals.post_save.connect(StudentYearGrade.build_all_cache, sender=Student)


letter_grade_choices = (
    ("I", "Incomplete"),
    ("P", "Pass"),
    ("F", "Fail"),
    ("A", "A"),
    ("B", "B"),
    ("C", "C"),
    ("D", "D"),
    ("HP", "High Pass"),
    ("LP", "Low Pass"),
    ("M", "Missing"),
)


class Grade(models.Model):
    student = models.ForeignKey('sis.Student')
    course_section = models.ForeignKey('schedule.CourseSection')
    enrollment = models.ForeignKey('schedule.CourseEnrollment', blank=True, null=True)
    marking_period = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    date = models.DateField(auto_now=True, validators=settings.DATE_VALIDATORS)
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    override_final = models.BooleanField(default=False, help_text="Override final grade for marking period instead of calculating it.")
    comment = models.CharField(max_length=500, blank=True, validators=[grade_comment_length_validator])
    letter_grade = models.CharField(max_length=10, blank=True, null=True, help_text="Will override grade.", choices=letter_grade_choices)
    letter_grade_choices = letter_grade_choices

    class Meta:
        unique_together = (("student", "course_section", "marking_period"),)
        permissions = (
            ("change_own_grade", "Change grades for own class"),
            ('change_own_final_grade','Change final YTD grades for own class'),
        )

    def display_grade(self):
        """ Returns full spelled out grade such as Fail, Pass, 60.05, B"""
        return self.get_grade(display=True)

    def set_grade(self, grade, letter_grade=None, treat_as_percent=True):
        """ Set grade to decimal or letter
        If grade is less than 1 assume it's a percentage
        letter_grade: If specified it will allow both numeric and letter
        grades to be saved
        returns success (True or False)"""
        try:
            grade = Decimal(str(grade))
            if treat_as_percent is True and grade < 1:
                # assume grade is a percentage
                grade = grade * 100
            self.grade = grade
            self.letter_grade = letter_grade
            return True
        except decimal.InvalidOperation:
            grade = unicode.upper(unicode(grade)).strip()
            if grade in dict(self.letter_grade_choices):
                self.letter_grade = grade
                self.grade = None
                return True
            elif grade in ('', 'NONE'):
                self.grade = None
                self.letter_grade = None
                return True
            return False

    @staticmethod
    def validate_grade(grade):
        """ Determine if grade is valid or not """
        try:
            grade = Decimal(str(grade))
            if grade >= 0:
                return
            raise ValidationError('Grade must be above 0')
        except decimal.InvalidOperation:
            grade = unicode.upper(unicode(grade)).strip()
            if (grade in dict(letter_grade_choices) or
               grade in ('', 'NONE')):
                return
        raise ValidationError('Invalid letter grade.')

    def invalidate_cache(self):
        """ Invalidate any related caches """
        try:
            enrollment = self.course_section.courseenrollment_set.get(user=self.student)
            enrollment.flag_grade_as_stale()
            enrollment.flag_numeric_grade_as_stale()
        except ecwsp.schedule.models.CourseEnrollment.DoesNotExist:
            pass
        self.student.cached_gpa = self.student.calculate_gpa()
        if self.student.cached_gpa != "N/A":
            self.student.save()

    def optimized_grade_to_scale(self, letter):
        """ Optimized version of GradeScale.to_letter
        letter - True for letter grade, false for numeric (ex: 4.0 scale) """
        rule = GradeScaleRule.objects.filter(
                grade_scale__schoolyear__markingperiod=self.marking_period_id,
                min_grade__lte=self.grade,
                max_grade__gte=self.grade,
                ).first()
        if letter:
            return rule.letter_grade
        return rule.numeric_scale

    def get_grade(self, letter=False, display=False, rounding=None,
                  minimum=None, number=False, letter_and_number=False):
        """
        letter: Converts to a letter based on GradeScale
        display: For letter grade - Return display name instead of abbreviation.
        rounding: Numeric - round to this many decimal places.
        minimum: Numeric - Minimum allowed grade. Will not return lower than this.
        number: Consider stored numeric grade only
        Returns grade such as 90.03, P, or F
        """
        if self.letter_grade and not number:
            if display:
                return self.get_letter_grade_display()
            else:
                return self.letter_grade
        elif self.grade is not None:
            grade = self.grade
            if minimum:
                if grade < minimum:
                    grade = minimum
            if rounding != None:
                string = '%.' + str(rounding) + 'f'
                grade = string % float(str(grade))
            if letter is True or letter_and_number is True:
                try:
                    result = self.optimized_grade_to_scale(letter=True)
                    if letter_and_number is True:
                        result = '{} ({})'.format(grade, result)
                    return result
                except GradeScaleRule.DoesNotExist:
                    return "No Grade Scale"
            return grade
        else:
            return ""

    api_grade = property(get_grade, set_grade)

    def clean(self):
        ''' We must allow simulataneous letter and number grades. Grading mechanisms
        submit both; the number is used for calculations and the letter appears on
        reports. '''
        if self.marking_period_id == None:
            if Grade.objects.filter(
                    student=self.student,
                    course_section=self.course_section,
                    marking_period=None
                    ).exclude(id=self.id).exists():
                raise ValidationError('Student, Course Section, MarkingPeriod must be unique')

    def save(self, *args, **kwargs):
        if not self.enrollment:
            try:
                enrollment = ecwsp.schedule.models.CourseEnrollment.objects.get(
                    course_section = self.course_section,
                    user = self.student
                    )
                self.enrollment = enrollment
            except:
                logging.info("No enrollment exists for this student, this grade is useless!")

        super(Grade, self).save(*args, **kwargs)
        self.invalidate_cache()

    def delete(self, *args, **kwargs):
        super(Grade, self).delete(*args, **kwargs)
        self.invalidate_cache()

    def __unicode__(self):
        return unicode(self.get_grade(self))

    @staticmethod
    def get_scaled_multiple_mp_average(student, marking_periods, rounding=2):
        if (type(marking_periods) is list and
            marking_periods and
            type(marking_periods[0]) is ecwsp.schedule.models.MarkingPeriod):
            marking_periods = [ mp.id for mp in marking_periods ]

        enrollments = ecwsp.schedule.models.CourseEnrollment.objects.filter(
                user=student,
                course_section__course__course_type__weight__gt=0,
                course_section__marking_period__in=marking_periods)
        total_credits = 0.0
        num_courses = 0
        total_grade = 0.0
        for enrollment in enrollments.distinct():
            grade = enrollment.get_average_for_marking_periods(marking_periods, numeric=True)
            if grade != None:
                grade = float(grade)
                num_credits = float(enrollment.course_section.course.credits)
                if grade > 0:
                    # only add boost for non-failing grades
                    grade += float(enrollment.course_section.course.course_type.boost)
                total_grade += grade * num_credits
                total_credits += num_credits
                num_courses += 1
        if num_courses > 0:
            average = total_grade / total_credits
            return round_as_decimal(average, rounding)
        else:
            return None

    @staticmethod
    def populate_grade(student, marking_period, course_section):
        """
        make sure that each combination of Student/MarkingPeriod/CourseSection
        has a grade entity associated with it. If none exists, create one and
        set the course grade to "None". This method should be called on
        enrolling students to an exsiting course or creating a new course,
        or creating a new marking period, or creating a new cource section
        """
        grade_instance = Grade.objects.filter(
            student = student,
            course_section = course_section,
            marking_period = marking_period
        )
        if not grade_instance:
            new_grade = Grade(
                student = student,
                course_section = course_section,
                marking_period = marking_period,
                enrollment = ecwsp.schedule.models.CourseEnrollment.objects.get(
                    course_section = course_section,
                    user = student
                ),
                grade = None,
            )
            new_grade.save()

