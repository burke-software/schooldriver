from django.db import models
from django.contrib import messages
from django.conf import settings
from django_cached_field import CachedCharField, CachedDecimalField

from ecwsp.sis.models import Student
from ecwsp.administration.models import Configuration

from datetime import date, datetime, timedelta
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
    saturday = models.BooleanField(default=False, )
    sunday = models.BooleanField(default=False, )
    
    class Meta:
        ordering = ('-start_date',)
    
    def __unicode__(self):
        return unicode(self.name)
        
    def clean(self):
        from django.core.exceptions import ValidationError
        # Don't allow draft entries to have a pub_date.
        if self.start_date > self.end_date:
            raise ValidationError('Cannot end before starting!')
        
    def get_number_days(self, date=date.today()):
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
            current_day += timedelta(days=1)
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
    attendance_note = models.CharField(max_length=255, blank=True, help_text="This note will appear when taking attendance")
    year = models.ForeignKey('sis.GradeLevel', blank=True, null=True)
    exclude_days = models.ManyToManyField('Day', blank=True, \
        help_text="Student does not need to attend on this day. Note courses already specify meeting days, this field is for students who have a special reason to be away")
    grade = CachedCharField(max_length=8, blank=True, verbose_name="Final Course Grade",
			    editable=False)
    numeric_grade = CachedDecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    class Meta:
	unique_together = (("course", "user", "role"),)
        
    def save(self, *args, **kwargs):
        if not self.id and hasattr(self.user, 'student'):
            student = self.user.student
        super(CourseEnrollment, self).save(*args, **kwargs)
    
    def cache_grades(self):
	""" Set cache on both grade and numeric_grade """
	grade = self.calculate_grade_real()
	self.grade = grade
	if isinstance(grade, Decimal):
	    self.numeric_grade = grade
	else:
	    self.numeric_grade = None
	self.grade_recalculation_needed = False
	self.numeric_grade_recalculation_needed = False
	self.save()
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
	course_grades = self.course.grade_set.filter(student=self.user)
	if date_report:
	    course_grades = course_grades.filter(marking_period__end_date__lte=date_report)
	
	final = course_grades.filter(override_final=True).first()
	if final:
	    return final.get_grade()
	
	final = 0.0
	grades = course_grades.filter(letter_grade=None, grade__isnull=False).extra(select={
	    'weighted_grade':
		'grade * (select weight from schedule_markingperiod where schedule_markingperiod.id = marking_period_id)'
	})
	if grades:
	    for grade in grades:
		final += float(grade.weighted_grade)
	    final = final / grades.count()*1.0
	    return Decimal(final).quantize(Decimal("0.01"), ROUND_HALF_UP)
	
	# Letter Grade
	if ignore_letter == False:
	    grades = course_grades
	    if grades:
		total_weight = Decimal(0)
		for grade in grades:
		    get_grade =  grade.get_grade()
		    if get_grade == "I":
			return "I"
		    elif get_grade in ["P","HP","LP"]:
			final += float(100 * grade.marking_period.weight)
			total_weight += grade.marking_period.weight
		    elif get_grade in ['F', 'M']:
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
	return ''
    
    def set_cache_grade(self):
        """ Calculate and cache the final course grade for a student """
        cache_grade = self.course.calculate_final_grade(self.user)
        if cache_grade == None:
            self.cache_grade = ""
        else:
            self.cache_grade = cache_grade
        
    def delete(self, *args, **kwargs):
        if hasattr(self.user, 'student'):
            student = self.user.student
        super(CourseEnrollment, self).delete(*args, **kwargs)
    

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
    credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Credits effect gpa.")
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
    
    def get_grades(self):
        for grade in self.grade_set.all():
            setattr(grade, '_course_cache', self)
            yield grade
    
    def add_cohort(self, cohort):
        for student in cohort.student_set.all():
            enroll, created = CourseEnrollment.objects.get_or_create(user=student, course=self, role="student")
            if created: enroll.save()
    
    def get_enrolled_students(self, show_deleted=False):
        if show_deleted:
            return Student.objects.filter(courseenrollment__course=self)
        else:
            return Student.objects.filter(courseenrollment__course=self, is_active=True)
    
    def is_passing(self, student, date_report=None, cache_grade=None, cache_passing=None, cache_letter_passing=None):
        """ Is student passing course? """
        if cache_passing == None:
            pass_score = float(Configuration.get_or_default("Passing Grade", '70').value)
	else:
	    pass_score = cache_passing
        if cache_grade:
            grade = cache_grade
        else:
            grade = self.get_final_grade(student, date_report=date_report)
        try:
            if grade >= int(pass_score):
                return True
        except:
            pass_letters = Configuration.get_or_default("Letter Passing Grade", 'A,B,C,P').value
            if grade in pass_letters.split(','):
                return True
        return False
    
    def get_attendance_students(self):
        """ Should be one line of code. Sorry this is so aweful
        Couldn't figure out any other way """
        today, created = Day.objects.get_or_create(day=str(date.today().isoweekday()))
        all = Student.objects.filter(courseenrollment__course=self, is_active=True)
        exclude = Student.objects.filter(courseenrollment__course=self, is_active=True, courseenrollment__exclude_days=today)
        ids = []
        for id in exclude.values('id'):
            ids.append(int(id['id']))
        return all.exclude(id__in=ids)
    
    def get_credits_earned(self, student=None, date_report=None, include_latest_mid=False):
        """ Get credits earned based on current date.
        include_latest_mid = include the latest mid marking period grade but count it as half weight"""
        # If student is passed, check if they are even passing
        if student and not self.is_passing(student, date_report):
            return 0
        if date_report == None:
            mps = self.marking_period.all().order_by('start_date')
        else:
            mps = self.marking_period.filter(end_date__lt=date_report).order_by('start_date')
        total_mps = self.marking_period.all().count()
        if include_latest_mid:
            credits = ((float(mps.count()) + 0.5) / float(total_mps)) * float(self.credits)
        else:
            credits = (float(mps.count()) / float(total_mps)) * float(self.credits)
        if self.credits < credits:
            credits = self.credits
        return credits
    
    def get_final_grade(self, student, date_report=None):
        """ Get final grade for a course. Returns override value if available.
	Uses cache is possible. Do not use in cache calculations!
        date_report: optional gets grade for time period"""
        if 'ecwsp.grades' in settings.INSTALLED_APPS:
            if not date_report or date_report == date.today():
                try:
                    enrollments = self.courseenrollment_set.get(user=student, role="student")
                    return enrollments.grade
                except CourseEnrollment.DoesNotExist:
                    pass
            return self.calculate_final_grade(student=student, date_report=date_report)

    
    def calculate_final_grade(self, student, date_report=None):
        """
        Calculates final grade.
        Note that this should match recalc_ytd_grade in gradesheet.js!
	Does NOT use cache!
        """
	course_enrollment = self.courseenrollment_set.get(user=student, role="student")
	return course_enrollment.calculate_grade_real(date_report=date_report)
    
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
    year = models.ForeignKey('sis.SchoolYear', help_text="Omit this year from GPA calculations and transcripts")
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
