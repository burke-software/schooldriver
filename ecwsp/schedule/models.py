from django.db import models
from django.contrib import messages
from django.conf import settings
from django_cached_field import CachedCharField, CachedDecimalField
from django.db import connection

from ecwsp.sis.models import Student
from ecwsp.sis.helper_functions import round_as_decimal
from ecwsp.administration.models import Configuration
import ecwsp

import datetime
from decimal import Decimal, ROUND_HALF_UP
import copy

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
    course = models.ForeignKey('Course')
    day_choice = (   # ISOWEEKDAY
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
        ('7', 'Sunday'),
    )
    day = models.CharField(max_length=1, choices=day_choice)
    location = models.ForeignKey('Location', blank=True, null=True)


class Location(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class CourseEnrollment(models.Model):
    course = models.ForeignKey('Course')
    user = models.ForeignKey('auth.User')
    role = models.CharField(max_length=255, default="Student", blank=True)
    attendance_note = models.CharField(max_length=255, blank=True, help_text="This note will appear when taking attendance.")
    year = models.ForeignKey('sis.GradeLevel', blank=True, null=True)
    exclude_days = models.ManyToManyField('Day', blank=True, \
        help_text="Student does not need to attend on this day. Note courses already specify meeting days; this field is for students who have a special reason to be away.")
    grade = CachedCharField(max_length=8, blank=True, verbose_name="Final Course Grade", editable=False)
    numeric_grade = CachedDecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (("course", "user", "role"),)

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
        self.save()
        return grade

    def get_grade(self, date_report=None, rounding=2):
        """ Get the grade, use cache when no date change present
        """
        if date_report is None or date_report >= datetime.date.today():
            # Cache will always have the latest grade, so it's fine for
            # today's date and any future date
            grade = self.grade
        else:
            grade = self.calculate_grade_real(date_report=date_report)
        if rounding and isinstance(grade, (int, long, float, complex, Decimal)):
            return round_as_decimal(grade, rounding)
        return grade

    def calculate_grade(self):
        return self.cache_grades()

    def calculate_numeric_grade(self):
        grade = self.cache_grades()
        if isinstance(grade, Decimal):
            return grade
        return None

    def calculate_grade_real(self, date_report=None, ignore_letter=False):
        """ Calculate the final grade for a course
        ignore_letter can be useful when computing averages
        when you don't care about letter grades
        """
        cursor = connection.cursor()

        # postgres requires a over () to run
        # http://stackoverflow.com/questions/19271646/how-to-make-a-sum-without-group-by
        sql_string = '''
SELECT ( Sum(grade * weight) {over} / Sum(weight) {over} ) AS ave_grade,
       grades_grade.id,
       grades_grade.override_final
FROM   grades_grade
       LEFT JOIN schedule_markingperiod
              ON schedule_markingperiod.id = grades_grade.marking_period_id
WHERE  ( grades_grade.course_id = %s
         AND grades_grade.student_id = %s {extra_where} )
       AND ( grade IS NOT NULL
              OR letter_grade IS NOT NULL )
ORDER  BY grades_grade.override_final DESC limit 1'''

        if date_report:
            if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
                cursor.execute(sql_string.format(
                    over='over ()', extra_where='AND (schedule_markingperiod.end_date <= %s OR override_final = 1)'),
                               (self.course_id, self.user_id, date_report))
            else:
                cursor.execute(sql_string.format(
                    over='', extra_where='AND (schedule_markingperiod.end_date <= %s OR grades_grade.override_final = 1)'),
                               (self.course_id, self.user_id, date_report))

        else:
            if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
                cursor.execute(sql_string.format(
                    over='over ()', extra_where=''),
                               (self.course_id, self.user_id))
            else:
                cursor.execute(sql_string.format(
                    over='', extra_where=''),
                               (self.course_id, self.user_id))

        result = cursor.fetchone()
        if result:
            (ave_grade, grade_id, override_final) = result
        else: # No grades at all. The average of no grades is None
            return None

        if override_final:
            course_grades = ecwsp.grades.models.Grade.objects.get(id=grade_id)
            grade = course_grades.get_grade()
            if ignore_letter and not isinstance(grade, (int, Decimal, float)):
                return None
            return grade

        if ave_grade:
            # database math always comes out as a float :(
            return Decimal(ave_grade)

        # about 0.5 s
        # Letter Grade
        if ignore_letter == False:
            final = 0.0
            grades = self.course.grade_set.filter(student=self.user)
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
                        final += get_grade
                if total_weight:
                    final /= float(total_weight)
                    final = Decimal(final).quantize(Decimal("0.01"), ROUND_HALF_UP)
                    if final > int(Configuration.get_or_default('letter_grade_required_for_pass').value):
                        return "P"
                    else:
                        return "F"
        return None


class Day(models.Model):
    dayOfWeek = (
        ("1", 'Monday'),
        ("2", 'Tuesday'),
        ("3", 'Wednesday'),
        ("4", 'Thursday'),
        ("5", 'Friday'),
        ("6", 'Saturday'),
        ("7", 'Sunday'),
    )
    day = models.CharField(max_length=1, choices=dayOfWeek)
    def __unicode__(self):
        return self.get_day_display()
    class Meta:
        ordering = ('day',)

class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
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

class Course(models.Model):
    active = models.BooleanField(default=True, help_text="Sometimes used in third party integrations such as Moodle. Has no affect within django-sis.")
    fullname = models.CharField(max_length=255, unique=True)
    shortname = models.CharField(max_length=255)
    marking_period = models.ManyToManyField(MarkingPeriod, blank=True)
    periods = models.ManyToManyField(Period, blank=True, through=CourseMeet)
    teacher = models.ForeignKey('sis.Faculty', blank=True, null=True, related_name="ateacher")
    secondary_teachers = models.ManyToManyField('sis.Faculty', blank=True, null=True, related_name="secondary_teachers")
    homeroom = models.BooleanField(default=False, help_text="Homerooms can be used for attendance")
    graded = models.BooleanField(default=True, help_text="Teachers can submit grades for this course")
    enrollments = models.ManyToManyField('auth.User', through=CourseEnrollment, blank=True, null=True)
    description = models.TextField(blank=True)
    credits = models.DecimalField(max_digits=5, decimal_places=2,
        help_text="Credits affect GPA.",
        default=lambda: Configuration.get_or_default(name='Default course credits').value)
    department = models.ForeignKey(Department, blank=True, null=True)
    level = models.ForeignKey('sis.GradeLevel', blank=True, null=True)
    last_grade_submission = models.DateTimeField(blank=True, null=True, editable=False, validators=settings.DATE_VALIDATORS)

    def __unicode__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        super(Course, self).save(*args, **kwargs)
        # assign teacher in as enrolled user
        try:
            if self.teacher:
                enroll, created = CourseEnrollment.objects.get_or_create(course=self, user=self.teacher, role="teacher")
        except: pass

    @staticmethod
    def autocomplete_search_fields():
        return ("shortname__icontains", "fullname__icontains",)

    def grades_link(self):
       link = '<a href="/grades/teacher_grade/upload/%s" class="historylink"> Grades </a>' % (self.id,)
       return link
    grades_link.allow_tags = True

    def calculate_final_grade(self, student):
        """ Shim code to calculate final grade WITHOUT cache """
        enrollment = self.courseenrollment_set.get(user=student, role="student")
        return enrollment.calculate_grade_real()

    def get_enrolled_students(self):
        return Student.objects.filter(courseenrollment__course=self)

    def copy_instance(self, request):
        changes = (("fullname", self.fullname + " copy"),)
        new = duplicate(self, changes)
        for enroll in self.courseenrollment_set.all():
            new_enrollment = CourseEnrollment(course=new, user=enroll.user, role=enroll.role, attendance_note=enroll.attendance_note)
            new_enrollment.save()
            for day in enroll.exclude_days.all():
                new_enrollment.exclude_days.add(day)
        for cm in self.coursemeet_set.all():
            new.coursemeet_set.create(location=cm.location,day=cm.day,period=cm.period)
        new.save()
        messages.success(request, 'Copy successful!')

    def number_of_students(self):
        return self.courseenrollment_set.filter(role="student").count()
    number_of_students.short_description = "# of Students"

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
