from django.db import models
from django.db.models.fields.related import ForeignKey
from django.db.models import Max
from django.contrib import messages
from django.conf import settings

from ecwsp.sis.models import Student
from ecwsp.administration.models import Configuration

from datetime import date, datetime
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
    start_date = models.DateField()
    end_date = models.DateField()
    school_year = models.ForeignKey('sis.SchoolYear')
    active = models.BooleanField(help_text="Teachers may only enter grades for active marking periods. There may be more than one active marking period.")
    show_reports = models.BooleanField(default=True, help_text="If checked this marking period will show up on reports.")
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True) 
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    
    class Meta:
        ordering = ('-start_date',)
    
    def __unicode__(self):
        return unicode(self.name)
        
        
class DaysOff(models.Model):
    date = models.DateField()
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
    user = models.ForeignKey('sis.MdlUser')
    role = models.CharField(max_length=255, default="Student", blank=True)
    attendance_note = models.CharField(max_length=255, blank=True, help_text="This note will appear when taking attendance")
    year = models.ForeignKey('sis.GradeLevel', blank=True, null=True)
    exclude_days = models.ManyToManyField('Day', blank=True, \
        help_text="Student does not need to attend on this day. Note courses already specify meeting days, this field is for students who have a special reason to be away")

    class Meta:
        unique_together = (("course", "user", "role"),)
        
    def save(self, *args, **kwargs):
        if not self.id and self.course.asp and hasattr(self.user, 'student'):
            student = self.user.student
            from ecwsp.sis.models import ASPHistory
            asp = ASPHistory(student=student, asp=self.course.shortname, enroll=True)
            asp.save()
        super(CourseEnrollment, self).save(*args, **kwargs)
        
        
    def delete(self, *args, **kwargs):
        if self.course.asp and hasattr(self.user, 'student'):
            student = self.user.student
            from ecwsp.sis.models import ASPHistory
            asp = ASPHistory(student=student, asp=self.course.shortname)
            asp.save()
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
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ('order_rank', 'name',)

class Course(models.Model):
    active = models.BooleanField(help_text="If active, course will show in Moodle.")
    fullname = models.CharField(max_length=255, unique=True)
    shortname = models.CharField(max_length=255)
    marking_period = models.ManyToManyField(MarkingPeriod, blank=True)
    periods = models.ManyToManyField(Period, blank=True, through=CourseMeet)
    teacher = models.ForeignKey('sis.Faculty', blank=True, null=True, related_name="ateacher")
    secondary_teachers = models.ManyToManyField('sis.Faculty', blank=True, null=True, related_name="secondary_teachers")
    homeroom = models.BooleanField(help_text="Homerooms can be used for attendance")
    asp = models.BooleanField(help_text="ASP, requires seperate attendance")
    enrollments = models.ManyToManyField('sis.MdlUser', through=CourseEnrollment, blank=True, null=True)
    description = models.TextField(blank=True)
    credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Credits effect gpa.")
    department = models.ForeignKey(Department, blank=True, null=True)
    level = models.ForeignKey('sis.GradeLevel', blank=True, null=True)
    
    def __unicode__(self):
        return self.fullname
    
    def save(self, *args, **kwargs):
        super(Course, self).save(*args, **kwargs)
        # assign teacher in as enrolled user
        try:
            if self.teacher:
                enroll, created = CourseEnrollment.objects.get_or_create(course=self, user=self.teacher, role="teacher")
        except: pass
    
    def grades_link(self):
       link = '<a href="/schedule/teacher_grade/upload/%s" class="historylink"> Grades </a>' % (self.id,)
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
            return Student.objects.filter(courseenrollment__course=self, inactive=False)
    
    def is_passing(self, student, date_report=None):
        """ Is student passing course? """
        pass_score = Configuration.get_or_default("Passing Grade", '70').value
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
        all = Student.objects.filter(courseenrollment__course=self, inactive=False)
        exclude = Student.objects.filter(courseenrollment__course=self, inactive=False, courseenrollment__exclude_days=today)
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
        date_report: optional gets grade for time period"""
        final = Grade.objects.filter(course=self, override_final=True, student=student)
        if final.count():
            if not date_report or final[0].course.marking_period.filter(end_date__lte=date_report).count():
                final = final[0].get_grade()
        else:
            final = self.calculate_final_grade(student, date_report)
        return final
    
    def calculate_final_grade(self, student, date_report=None):
        """ Calculates final grade. Does not take into account overrides. """
        final = Decimal(0)
        number = 0
        grades =  Grade.objects.filter(student=student, final=True, course=self)
        if date_report:
            grades = grades.filter(marking_period__end_date__lte=date_report)
        for grade in grades:
            try:
                final += grade.get_grade()
                number += 1
            # otherwise it's a letter grade.
            except: pass
        if number != 0:
            final = final / number
            final = Decimal(final).quantize(Decimal("0.01"), ROUND_HALF_UP)
        else:
            final = None
        return final
    
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
        
    def clean(self):
        from django.core.exceptions import ValidationError
        if settings.ASP and self.homeroom and self.asp:
            raise ValidationError('Cannot be both homeroom and asp.')
    
    def generate_moodle_events(self):
        pass
        

class GradeComment(models.Model):
    id = models.IntegerField(primary_key=True)
    comment = models.CharField(max_length=500)
    
    def __unicode__(self):
        return unicode(self.id) + ": " + unicode(self.comment)
        
    class Meta:
        ordering = ('id',)
        
class OmitCourseGPA(models.Model):
    """ Used to keep repeated or invalid course from affecting GPA """
    student = models.ForeignKey('sis.Student')
    course = models.ForeignKey(Course)
    def __unicode__(self):
        return "%s %s" % (self.student, self.course)

class Grade(models.Model):
    student = models.ForeignKey('sis.Student')
    course = models.ForeignKey(Course)
    marking_period = models.ForeignKey(MarkingPeriod, blank=True, null=True)
    date = models.DateField(auto_now=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    final = models.BooleanField(help_text="Yes for final grade. No for mid marking period report. Only final grades are included in the average.")
    override_final = models.BooleanField(help_text="Override final grade for marking period instead of calculating it.")
    comment = models.CharField(max_length=500, blank=True)
    letter_grade_choices = (
            ("I", "Incomplete"),
            ("P", "Pass"),
            ("F", "Fail"),
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        )
    letter_grade = models.CharField(max_length=1, blank=True, null=True, help_text="Will override grade.", choices=letter_grade_choices)
    
    class Meta:
        unique_together = (("student", "course", "marking_period", "final"),)
        permissions = (
            ("change_own_grade", "Change grades for own class"),
        )
        
    def display_grade(self):
        """ Returns full spelled out grade such as Fail, Pass, 60.05, B"""
        return self.get_grade(display=True)
    
    def set_grade(self, grade):
        """ set grade to decimal or letter 
            if grade is less than 1 assume it's a percentage
            returns success (True or False)"""
        try:
            grade = Decimal(str(grade))
            if grade <= 1:
                # assume grade is a percentage
                grade = grade * 100
            self.grade = grade
            self.letter_grade = None
            return True
        except:
            grade = unicode.upper(unicode(grade)).strip()
            if grade in dict(self.letter_grade_choices):
                self.letter_grade = grade
                self.grade = None
                return True
            elif grade in ('', None, 'None'):
                self.grade = None
                self.letter_grade = None
                return True
            return False
    
    def get_grade(self, letter=False, display=False, rounding=None):
        """ By default returns simple grade such as 90.03, P, or F"""
        if self.letter_grade:
            if display:
                return self.get_letter_grade_display()
            else:
                return self.letter_grade
        elif self.grade:
            if rounding != None:
                string = '%.' + str(rounding) + 'f'
                return string % float(str(self.grade))
            else:
                return self.grade
        else:
            return ""
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.grade and self.letter_grade != None:
            raise ValidationError('Cannot have both numeric and letter grade')
    
    def save(self, *args, **kwargs):
        super(Grade, self).save(*args, **kwargs)
        
        #cache student's GPA
        if self.grade and self.student:
            self.student.cache_gpa = self.student.calculate_gpa()
            if self.student.cache_gpa != "N/A":
                self.student.save()
    
    def __unicode__(self):
        return unicode(self.get_grade(self))
        

class StandardTest(models.Model):
    """ A test such as SAT or ACT """
    name = models.CharField(max_length=255, unique=True)
    calculate_total = models.BooleanField(
        help_text = "Automatically calculate the total score by adding others together",
    )
    cherry_pick_categories = models.BooleanField(
        help_text="Cherry pick results to generate total. Goes through each category and picks best score. Then calculates the total.",
    )
    cherry_pick_final = models.BooleanField("Cherry pick results to get total. Only use final scores.")
    show_on_reports = models.BooleanField(default=True)
    
    def __unicode__(self):
        return unicode(self.name)
        
    def get_cherry_pick_total(self, student):
        """ Returns cherry
        Why show real grades, when fake ones that look better?
        """
        cherry = 0
        if self.cherry_pick_final:
            for result in self.standardtestresult_set.filter(student=student):
                cat_total = result.standardcategorygrade_set.get(category__is_total=True)
                if cat_total > cherry: cherry = cat_total.grade
        elif self.cherry_pick_categories:
            cats = self.standardcategory_set.filter(standardcategorygrade__result__student=student).annotate(highest=Max('standardcategorygrade__grade'))
            for cat in cats:
                cherry += cat.highest
        return cherry
        

class StandardCategory(models.Model):
    """ Category for a test """
    name = models.CharField(max_length=255)
    test = models.ForeignKey(StandardTest)
    is_total = models.BooleanField(
        help_text="This is actually the total. Use this for tests that do not use simple addition to calculate final scores",
    )
    def __unicode__(self):
        return unicode(self.test) + ": " + unicode(self.name)

class StandardTestResult(models.Model):
    """ Standardized test instance. This is the results of a student taking a test """
    date = models.DateField(default=date.today())
    student = models.ForeignKey('sis.Student')
    test = models.ForeignKey(StandardTest)
    def __unicode__(self):
        try:
            return '%s %s %s' % (unicode(self.student), unicode(self.test), self.date)
        except:
            return "Standard Test Result"
    
    @property
    def total(self):
        """Returns total for the test instance
        This may be calculated or marked as "is_total" on the category
        """
        if self.test.calculate_total:
            total = 0
            for cat in self.standardcategorygrade_set.all():
                total += cat.grade
            return total
        elif self.standardcategorygrade_set.filter(category__is_total=True):
            totals = self.standardcategorygrade_set.filter(category__is_total=True)
            if totals:
                return totals[0].grade
        else:
            return None

class StandardCategoryGrade(models.Model):
    """ Grade for a category and result """
    category = models.ForeignKey(StandardCategory)
    result = models.ForeignKey(StandardTestResult)
    grade = models.IntegerField()


class Award(models.Model):
    name = models.CharField(max_length=255)

class AwardStudent(models.Model):
    award = models.ForeignKey(Award)
    student = models.ForeignKey('sis.Student')
    marking_period = models.ForeignKey(MarkingPeriod, blank=True, null=True)