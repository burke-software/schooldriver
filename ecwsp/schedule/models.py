from django.contrib import messages
from django.conf import settings
from django_cached_field import CachedCharField, CachedDecimalField
from django.db import connection
from django.db import models
from django.db.models.query import QuerySet
from django.core.urlresolvers import reverse

from ecwsp.sis.models import Student, GradeScaleRule
from ecwsp.sis.helper_functions import round_as_decimal, round_to_standard
from ecwsp.grades.models import Grade
from ecwsp.administration.models import Configuration
from constance import config

import datetime
import decimal
from decimal import Decimal, ROUND_HALF_UP
import copy

ISOWEEKDAY_TO_VERBOSE = (
    ("1", 'Monday'),
    ("2", 'Tuesday'),
    ("3", 'Wednesday'),
    ("4", 'Thursday'),
    ("5", 'Friday'),
    ("6", 'Saturday'),
    ("7", 'Sunday'),
)

def duplicate(obj, changes=None):
    """ Duplicates any object including m2m fields
    changes: any changes that should occur, example
    changes = (('fullname','name (copy)'), ('do not copy me', ''))"""
    if not obj.pk:
        raise ValueError('Instance must be saved before it can be cloned.')
    duplicate = copy.copy(obj)
    duplicate.pk = None
    for change in changes:
        duplicate.__setattr__(change[0], change[1])
    duplicate.save()
    # trick to copy ManyToMany relations.
    for field in obj._meta.many_to_many:
        source = getattr(obj, field.attname)
        destination = getattr(duplicate, field.attname)
        for item in source.all():
            try: # m2m, through fields will fail.
                destination.add(item)
            except: pass
    return duplicate

class MarkingPeriod(models.Model):
    name = models.CharField(max_length=255, unique=True)
    shortname = models.CharField(max_length=255)
    start_date = models.DateField(validators=settings.DATE_VALIDATORS)
    end_date = models.DateField(validators=settings.DATE_VALIDATORS)
    grades_due = models.DateField(validators=settings.DATE_VALIDATORS, blank=True, null=True,
                                  help_text="If filled out, teachers will be notified when grades are due.")
    school_year = models.ForeignKey('sis.SchoolYear')
    active = models.BooleanField(default=False, help_text="Teachers may only enter grades for active marking periods. There may be more than one active marking period.")
    show_reports = models.BooleanField(default=True, help_text="If checked this marking period will show up on reports.")
    school_days = models.IntegerField(blank=True, null=True, help_text="If set, this will be the number of days school is in session. If unset, the value is calculated by the days off.")
    weight = models.DecimalField(max_digits=5, decimal_places=3, default=1, help_text="Weight for this marking period when calculating grades.")
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    class Meta:
        ordering = ('-start_date',)

    def __unicode__(self):
        return unicode(self.name)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Don't allow draft entries to have a pub_date.
        if self.start_date > self.end_date:
            raise ValidationError('Cannot end before starting!')

    def save(self, **kwargs):
        obj = super(MarkingPeriod, self).save(**kwargs)
        if 'ecwsp.grades' in settings.INSTALLED_APPS:
            from ecwsp.grades.tasks import build_grade_cache
            build_grade_cache.apply_async()
        return obj

    def get_number_days(self, date=datetime.date.today()):
        """ Get number of days in a marking period"""
        if (self.school_days or self.school_days == 0) and date >= self.end_date:
            return self.school_days
        day = 0
        current_day = self.start_date
        while current_day <= date:
            is_day = False
            if current_day >= self.start_date and current_day <= self.end_date:
                days_off = []
                for d in self.daysoff_set.all().values_list('date'): days_off.append(d[0])
                if not current_day in days_off:
                    if self.monday and current_day.isoweekday() == 1:
                        is_day = True
                    elif self.tuesday and current_day.isoweekday() == 2:
                        is_day = True
                    elif self.wednesday and current_day.isoweekday() == 3:
                        is_day = True
                    elif self.thursday and current_day.isoweekday() == 4:
                        is_day = True
                    elif self.friday and current_day.isoweekday() == 5:
                        is_day = True
                    elif self.saturday and current_day.isoweekday() == 6:
                        is_day = True
                    elif self.sunday and current_day.isoweekday() == 7:
                        is_day = True
            if is_day: day += 1
            current_day += datetime.timedelta(days=1)
        return day

class DaysOff(models.Model):
    date = models.DateField(validators=settings.DATE_VALIDATORS)
    marking_period = models.ForeignKey(MarkingPeriod)

    def __unicode__(self):
        return unicode(self.date)


class Period(models.Model):
    name = models.CharField(max_length=255, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ('start_time',)

    def __unicode__(self):
        return "%s %s-%s" % (self.name, self.start_time.strftime('%I:%M%p'), self.end_time.strftime('%I:%M%p'))

class CourseMeet(models.Model):
    period = models.ForeignKey(Period)
    course_section = models.ForeignKey('CourseSection')
    day = models.CharField(max_length=1, choices=ISOWEEKDAY_TO_VERBOSE)
    location = models.ForeignKey('Location', blank=True, null=True)
    day_choice = ISOWEEKDAY_TO_VERBOSE


class Location(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class CourseEnrollment(models.Model):
    course_section = models.ForeignKey('CourseSection')
    user = models.ForeignKey('sis.Student')
    attendance_note = models.CharField(max_length=255, blank=True, help_text="This note will appear when taking attendance.")
    exclude_days = models.CharField(max_length=100, blank=True,
        help_text="Student does not need to attend on this day. Note course sections already specify meeting days; this field is for students who have a special reason to be away.")
    grade = CachedCharField(max_length=8, blank=True, verbose_name="Final Course Section Grade", editable=False)
    numeric_grade = CachedDecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)


    class Meta:
        unique_together = (("course_section", "user"),)

    def save(self, populate_all_grades=True, *args, **kwargs):
        """ populate_all_grades (default True) is intended to
        recalculate any related grades to this enrollment.
        It can be disabled to stop a recursive save.
        """
        super(CourseEnrollment, self).save(*args, **kwargs)
        if populate_all_grades is True:
            self.course_section.populate_all_grades()

    def cache_grades(self):
        """ Set cache on both grade and numeric_grade """
        grade = self.calculate_grade_real()
        if isinstance(grade, Decimal):
            grade = grade.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
            self.numeric_grade = grade
        else:
            self.numeric_grade = None
        if grade == None:
            grade = ''
        self.grade = grade
        self.grade_recalculation_needed = False
        self.numeric_grade_recalculation_needed = False
        self.save(populate_all_grades=False)  # Causes recursion otherwise.
        return grade

    def get_average_for_marking_periods(self, marking_periods, letter=False, numeric=False):
        """ Get the average for only some marking periods
        marking_periods - Queryset or optionally pass ids only as an optimization
        letter - Letter grade scale
        numeric - non linear numeric scale
        """
        if isinstance(marking_periods, QuerySet):
            marking_periods = tuple(marking_periods.values_list('id', flat=True))
        else:
            # Check marking_periods because we can't use sql parameters because sqlite and django suck
            if all(isinstance(item, int) for item in marking_periods) != True:
                raise ValueError('marking_periods must be list or tuple of ints')
            marking_periods = tuple(marking_periods)

        cursor = connection.cursor()
        sql_string = '''
SELECT Sum(grade * weight) {over} / Sum(weight) {over} AS ave_grade FROM grades_grade
LEFT JOIN schedule_markingperiod
    ON schedule_markingperiod.id = grades_grade.marking_period_id
WHERE grades_grade.course_section_id = %s
    AND grades_grade.student_id = %s
    AND schedule_markingperiod.id in {marking_periods}
    AND ( grade IS NOT NULL OR letter_grade IS NOT NULL )'''
        if settings.DATABASES['default']['ENGINE'] in ['django.db.backends.postgresql_psycopg2', 'tenant_schemas.postgresql_backend']:
            sql_string = sql_string.format(over='over ()', marking_periods=marking_periods)
        else:
            sql_string = sql_string.format(over='', marking_periods=marking_periods)

        cursor.execute(sql_string, (self.course_section_id, self.user_id))
        result = cursor.fetchone()
        if result:
            grade = result[0]
        else:
            return None
        if grade is not None:
            if letter:
                grade = self.optimized_grade_to_scale(grade, letter=True)
            elif numeric:
                grade = self.optimized_grade_to_scale(grade, letter=False)
        return grade

    def optimized_grade_to_scale(self, grade, letter=True):
        """ letter - True for letter grade, false for numeric (ex: 4.0 scale) """

        # not sure how this was working before, but I'm just commenting it out
        # if something else relies on the old method I have just broke it!
        # -Q
        '''rule = GradeScaleRule.objects.filter(
            grade_scale__schoolyear__markingperiod__coursesection=self,
            min_grade__lte=grade,
            max_grade__gte=grade).first()'''
        grade = round_to_standard(grade)
        rule = GradeScaleRule.objects.filter(
            min_grade__lte=grade,
            max_grade__gte=grade,
            ).select_related('course_section').first()
        if letter:
            return rule.letter_grade
        return rule.numeric_scale

    def get_grade(self, date_report=None, rounding=2, letter=False):
        """ Get the grade, use cache when no date change present
        date_report:
        rounding: Round to this many decimal places
        letter: Convert to letter grade scale
        """
        if date_report is None or date_report >= datetime.date.today():
            # Cache will always have the latest grade, so it's fine for
            # today's date and any future date
            if self.numeric_grade:
                grade = self.numeric_grade
            else:
                grade = self.grade
        else:
            grade = self.calculate_grade_real(date_report=date_report)
        if rounding and isinstance(grade, (int, long, float, complex, Decimal)):
            grade = round_as_decimal(grade, rounding)
        if letter == True and isinstance(grade, (int, long, float, complex, Decimal)):
            return self.optimized_grade_to_scale(grade)
        return grade

    def calculate_grade(self):
        return self.cache_grades()

    def calculate_numeric_grade(self):
        grade = self.cache_grades()
        if isinstance(grade, Decimal):
            return grade
        return None

    def calculate_grade_real(self, date_report=None, ignore_letter=False):
        """ Calculate the final grade for a course section
        ignore_letter can be useful when computing averages
        when you don't care about letter grades
        """
        cursor = connection.cursor()

        # postgres requires a over () to run
        # http://stackoverflow.com/questions/19271646/how-to-make-a-sum-without-group-by
        sql_string = '''
SELECT case when Sum(override_final{postgres_type_cast}) {over} = 1 then -9001 else (Sum(grade * weight) {over} / Sum(weight) {over}) end AS ave_grade
FROM grades_grade
    LEFT JOIN schedule_markingperiod
    ON schedule_markingperiod.id = grades_grade.marking_period_id
WHERE (grades_grade.course_section_id = %s
    AND grades_grade.student_id = %s {extra_where} )
    AND ( grade IS NOT NULL
    OR letter_grade IS NOT NULL )'''

        if date_report:
            if settings.DATABASES['default']['ENGINE'] in ['django.db.backends.postgresql_psycopg2', 'tenant_schemas.postgresql_backend']:
                cursor.execute(sql_string.format(
                    postgres_type_cast='::int', over='over ()', extra_where='AND (schedule_markingperiod.end_date <= %s OR override_final = true)'),
                               (self.course_section_id, self.user_id, date_report))
            else:
                cursor.execute(sql_string.format(
                    postgres_type_cast='', over='', extra_where='AND (schedule_markingperiod.end_date <= %s OR grades_grade.override_final = true)'),
                               (self.course_section_id, self.user_id, date_report))

        else:
            if settings.DATABASES['default']['ENGINE'] in ['django.db.backends.postgresql_psycopg2', 'tenant_schemas.postgresql_backend']:
                cursor.execute(sql_string.format(
                    postgres_type_cast='::int', over='over ()', extra_where=''),
                               (self.course_section_id, self.user_id))
            else:
                cursor.execute(sql_string.format(
                    postgres_type_cast='', over='', extra_where=''),
                               (self.course_section_id, self.user_id))

        result = cursor.fetchone()
        if result:
            ave_grade = result[0]
        else: # No grades at all. The average of no grades is None
            return None

        # -9001 = override. We can't mix text and int in picky postgress.
        if str(ave_grade) == "-9001":
            course_section_grade = Grade.objects.get(override_final=True, student=self.user, course_section=self.course_section)
            grade = course_section_grade.get_grade()
            if ignore_letter and not isinstance(grade, (int, Decimal, float)):
                return None
            return grade

        elif ave_grade:
            return Decimal(ave_grade)

        # about 0.5 s
        # Letter Grade
        if ignore_letter == False:
            final = 0.0
            grades = self.course_section.grade_set.filter(student=self.user)
            if date_report:
                grades = grades.filter(marking_period__end_date__lte=date_report)
            if grades:
                total_weight = Decimal(0)
                for grade in grades:
                    get_grade =  grade.get_grade()
                    if get_grade in ["I", "IN", "YT"]:
                        return get_grade
                    elif get_grade in ["P","HP","LP"]:
                        if grade.marking_period:
                            final += float(100 * grade.marking_period.weight)
                            total_weight += grade.marking_period.weight
                    elif get_grade in ['F', 'M']:
                        if grade.marking_period:
                            total_weight += grade.marking_period.weight
                    elif get_grade:
                        try:
                            final += get_grade
                        except TypeError:
                            return get_grade
                if total_weight:
                    final /= float(total_weight)
                    final = Decimal(final).quantize(Decimal("0.01"), ROUND_HALF_UP)
                    if final > config.LETTER_GRADE_REQUIRED_FOR_PASS:
                        return "P"
                    else:
                        return "F"
        return None


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Department Name")
    order_rank = models.IntegerField(blank=True, null=True, help_text="Rank that courses will show up in reports")
    def get_graduation_credits(self, student):
        try:
            # We have a credits requirement explicitly matching this student's class year
            graduation_credits_object = self.departmentgraduationcredits_set.get(class_year=student.class_of_year)
        except DepartmentGraduationCredits.DoesNotExist:
            # No explicit match, so find the most recent requirement that went into effect *before* this marking period's school year
            try:
                graduation_credits_object = self.departmentgraduationcredits_set.filter(class_year__year__lt=student.class_of_year.year).order_by('-class_year__year')[0]
            except IndexError:
                return None
        return graduation_credits_object.credits
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ('order_rank', 'name',)

class DepartmentGraduationCredits(models.Model):
    department = models.ForeignKey(Department)
    class_year = models.ForeignKey('sis.ClassYear', help_text='Also applies to subsequent years unless a more recent requirement exists.')
    credits = models.DecimalField(max_digits=5, decimal_places=2)
    class Meta:
        unique_together = ('department', 'class_year')

class CourseType(models.Model):
    ''' Some course types, e.g. honors or AP, may have uncommon settings.
    For consistency, the default data includes a "Normal" type. '''
    name = models.CharField(max_length=255, unique=True)
    is_default = models.BooleanField(default=False, help_text="Only one course " \
        "type can be the default.")
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1,
        help_text="A course's weight in average calculations is this value "
            "multiplied by the number of credits for the course. A course that "
            "does not affect averages should have a weight of 0, while an "
            "honors course might, for example, have a weight of 1.2.")
    award_credits = models.BooleanField(default=True,
        help_text="When disabled, course will not be included in any student's "
            "credit totals. However, the number of credits and weight will "
            "still be used when calculating averages.")
    boost = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    def save(self, *args, **kwargs):
        ''' If I am the default, no other CourseType can be! '''
        super(CourseType, self).save(*args, **kwargs)
        if self.is_default:
            CourseType.objects.exclude(pk=self.pk).update(is_default=False)
    def __unicode__(self):
        return self.name

    @staticmethod
    def build_default():
        """ Always reference this function when creating the default """
        return CourseType.objects.get_or_create(name='Normal-Test', is_default=True)[0]


def get_course_type_default():
    try:
        return CourseType.objects.get(is_default=True).pk
    except CourseType.DoesNotExist:
        return CourseType.build_default().pk

def get_credits_default():
    return Configuration.get_or_default(name='Default course credits').value

class Course(models.Model):
    is_active = models.BooleanField(default=True)
    fullname = models.CharField(max_length=255, unique=True, verbose_name="Full Course Name")
    shortname = models.CharField(max_length=255, verbose_name="Short Name")
    homeroom = models.BooleanField(default=False, help_text="Homerooms can be used for attendance")
    graded = models.BooleanField(default=True, help_text="Teachers can submit grades for this course")
    description = models.TextField(blank=True)
    credits = models.DecimalField(max_digits=5, decimal_places=2,
        help_text="Credits affect GPA.",
        # WARNING: this default must NOT be used for migrations! Courses whose
        # credits=None should have their credits set to 0
        default=get_credits_default)
    department = models.ForeignKey(Department, blank=True, null=True)
    level = models.ForeignKey('sis.GradeLevel', blank=True, null=True, verbose_name="Grade Level")
    course_type = models.ForeignKey(CourseType,
        help_text='Should only need adjustment when uncommon calculation ' \
        'methods are used.',
        default=get_course_type_default,
    )

    def __unicode__(self):
        return self.fullname

    @property
    def start_date(self):
        mp = MarkingPeriod.objects.filter(coursesection__course=self).order_by('start_date').first()
        if mp:
            return mp.start_date
    @property
    def end_date(self):
        mp = MarkingPeriod.objects.filter(coursesection__course=self).order_by('-end_date').first()
        if mp:
            return mp.end_date

    @staticmethod
    def autocomplete_search_fields():
        return ("shortname__icontains", "fullname__icontains",)

    def get_enrolled_students(self):
        return Student.objects.filter(courseenrollment__section=self)

class CourseSectionTeacher(models.Model):
    teacher = models.ForeignKey('sis.Faculty')
    course_section = models.ForeignKey('CourseSection')
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('teacher', 'course_section')

class CourseSection(models.Model):
    course = models.ForeignKey(Course, related_name='sections')
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    marking_period = models.ManyToManyField(MarkingPeriod, blank=True)
    periods = models.ManyToManyField(Period, blank=True, through=CourseMeet)
    teachers = models.ManyToManyField('sis.Faculty', through=CourseSectionTeacher, blank=True)
    enrollments = models.ManyToManyField('sis.Student', through=CourseEnrollment, blank=True, null=True)
    cohorts = models.ManyToManyField('sis.Cohort', blank=True, null=True)
    last_grade_submission = models.DateTimeField(blank=True, null=True, editable=False, validators=settings.DATE_VALIDATORS)

    def __unicode__(self):
        return u'{}: {}'.format(self.course, self.name)

    @property
    def department(self):
        return self.course.department

    @property
    def level(self):
        """ Course grade level """
        return self.course.level

    @property
    def credits(self):
        return self.course.credits

    @property
    def description(self):
        """ Course description """
        return self.course.description

    @property
    def fullname(self):
        """ Course full name """
        return self.course.fullname

    @property
    def shortname(self):
        """ Course short name """
        return self.course.shortname

    def get_todays_period(self):
        """ Useful if you want to know today's schedule """
        return self.periods.filter(coursemeet__day__exact=datetime.date.today().isoweekday()).first()


    @property
    def teacher(self):
        """ Show just the primary teacher, or any if there is no primary """
        course_teacher = self.coursesectionteacher_set.all().order_by('-is_primary').first()
        if course_teacher:
            return course_teacher.teacher

    def number_of_students(self):
        return self.enrollments.count()
    number_of_students.short_description = "# of Students"

    def grades_link(self):
        link = '<a href="{}" class="historylink"> Grades </a>'.format(
            reverse('course-section-grades', args=(self.pk,))
        )
        return link
    grades_link.allow_tags = True

    def calculate_final_grade(self, student):
        """ Shim code to calculate final grade WITHOUT cache """
        enrollment = self.courseenrollment_set.get(user=student)
        return enrollment.calculate_grade_real()

    def populate_all_grades(self):
        """
        calling this method calls Grade.populate_grade on each combination
        of enrolled_student + marking_period + course_section
        """
        for student in self.enrollments.all():
            for marking_period in self.marking_period.all():
                Grade.populate_grade(
                    student = student,
                    marking_period = marking_period,
                    course_section = self
                    )

    def save(self, *args, **kwargs):
        super(CourseSection, self).save(*args, **kwargs)
        ''' HEY, YOU! This save() method can't see any M2M changes!
        Read http://stackoverflow.com/a/1925784. To handle users changing the
        selected MarkingPeriods, I'm writing CourseSectionAdmin.save_model(),
        which will also call populate_all_grades(). You may need additional
        handling if you implement another edit interface outside of Django
        admin. '''
        self.populate_all_grades()

    def copy_instance(self, request):
        changes = (("name", self.name + " copy"),)
        new = duplicate(self, changes)
        for enroll in self.courseenrollment_set.all():
            new_enrollment = CourseEnrollment(
                course_section=new,
                user=enroll.user,
                attendance_note=enroll.attendance_note
            )
            new_enrollment.save()
            for day in enroll.exclude_days.all():
                new_enrollment.exclude_days.add(day)
        for cm in self.coursemeet_set.all():
            new.coursemeet_set.create(
                location=cm.location,
                day=cm.day,
                period=cm.period
            )
        for teacher in self.coursesectionteacher_set.all():
            CourseSectionTeacher(
                course_section=new,
                teacher=teacher.teacher,
                is_primary=teacher.is_primary
            ).save()
        new.save()
        messages.success(request, 'Copy successful!')

class OmitCourseGPA(models.Model):
    """ Used to keep repeated or invalid course from affecting GPA """
    student = models.ForeignKey('sis.Student')
    course = models.ForeignKey(Course)
    def __unicode__(self):
        return "%s %s" % (self.student, self.course)

class OmitYearGPA(models.Model):
    """ Used to keep repeated or invalid years from affecting GPA and transcripts """
    student = models.ForeignKey('sis.Student')
    year = models.ForeignKey('sis.SchoolYear', help_text="Omit this year from GPA calculations and transcripts.")
    def __unicode__(self):
        return "%s %s" % (self.student, self.year)


class Award(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return unicode(self.name)

class AwardStudent(models.Model):
    award = models.ForeignKey(Award)
    student = models.ForeignKey('sis.Student')
    marking_period = models.ForeignKey(MarkingPeriod, blank=True, null=True)
