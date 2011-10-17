#   Copyright 2010 Cristo Rey New York High School
#   Author David M Burke <david@burkesoftware.com>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#     
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#      
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from django.core.exceptions import ValidationError
from django.db import models
from django.db import connection
from django.db.models import Max
from django.db.models.signals import post_save, m2m_changed
from django.contrib.localflavor.us.models import *
from django.contrib.auth.models import User, Group
from django.conf import settings

import logging
from thumbs import ImageWithThumbsField
from datetime import date, timedelta, datetime
from decimal import *
import types

logger = logging.getLogger(__name__)

def create_faculty(instance):
    faculty, created = Faculty.objects.get_or_create(username=instance.username)
    if created:
        faculty.fname=instance.first_name
        faculty.lname=instance.last_name
        faculty.email=instance.email
        faculty.teacher=True
        faculty.save()

def create_faculty_profile(sender, instance, created, **kwargs):
    if instance.groups.filter(name="teacher").count():
        create_faculty(instance)

def create_faculty_profile_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add' and instance.groups.filter(name="teacher").count():
        create_faculty(instance)

post_save.connect(create_faculty_profile, sender=User)
m2m_changed.connect(create_faculty_profile_m2m, sender=User.groups.through)

class UserPreference(models.Model):
    """ User Preferences """
    file_format_choices = (
        ('o', 'Open Document Format (.odt, .ods)'),
        ('m', 'Microsoft Binary (.doc, .xls)'),
        ('x', 'Microsoft Office Open XML (.docx, .xlsx) Not recommended, formatting may be lost!'),
    )
    prefered_file_format = models.CharField(default=settings.PREFERED_FORMAT, max_length="1", choices=file_format_choices, help_text="Open Document recommened.") 
    include_deleted_students = models.BooleanField(help_text="When searching for students, include deleted (previous) students.")
    additional_report_fields = models.ManyToManyField('ReportField', blank=True, null=True, help_text="These fields will be added to spreadsheet reports. WARNING adding fields with multiple results will GREATLY increase the time it takes to generate reports")
    user = models.ForeignKey(User, unique=True, editable=False)
    names = None    # extra field names. (Attempt to speed up reports so these don't get called up over and over)
    first = True
    
    def get_format(self, type="document"):
        """ Return format extension. 
        type: type of format (document or spreadsheet) """
        if type == "document":
            if self.prefered_file_format == "o":
                return "odt"
            elif self.prefered_file_format == "m":
                return "doc"
            elif self.prefered_file_format == "x":
                return "docx"
        elif type == "spreadsheet":
            if self.prefered_file_format == "o":
                return "ods"
            elif self.prefered_file_format == "m":
                return "xls"
            elif self.prefered_file_format == "x":
                return "xlsx"
            
    def get_additional_student_fields(self, row, student, students, titles, buffer=1):
        """ row: table row """
        """Get additional fields based on user preferences"""
        if not self.names:
            self.set_names()
        for name in self.names:
            buffer = self.get_additional_student_fields_buffer(students, name)
            if self.first:
                i = 0
                while i < buffer:
                    titles.append(name)
                    i += 1
            space = 0
            try:
                many = False
                object = student
                for name_split in name.split('.'):
                    object = object.__getattribute__(name_split)
                    if str(object)[:51] == "<django.db.models.fields.related.ManyRelatedManager":
                        for one_of_many in object.all():
                            row.append(unicode(one_of_many))
                            space += 1
                            many = True
                if not many:
                    row.append(unicode(object))
                    space += 1
            except:
                row.append("")
                space += 1
            while space < buffer:
                row.append("")
                space += 1
        self.first = False
    
    def get_additional_student_fields_buffer(self, students, name):
        buffer = 1
        for student in students:
            try:
                object = student
                for name_split in name.split('.'):
                    object = object.__getattribute__(name_split)
                    if str(object)[:51] == "<django.db.models.fields.related.ManyRelatedManager":
                        number = object.all().count()
                        if number > buffer: buffer = number
            except:
                pass
        return buffer
                
    
    def set_names(self):
        fields = self.additional_report_fields.all()
        self.names = []
        for field in fields:    
            self.names.append(field.name)
        self.names


class ReportField(models.Model):
    name = models.CharField(unique=True, max_length=255)
    def __unicode__(self):
        return unicode(self.name)


class MdlUser(models.Model):
    """Generic person model. Named when it was though sword would depend
    heavily with Moodle. A person is any person in the school, such as a student
    or teacher. It's not a login user though may be related to a login user"""
    inactive = models.BooleanField()
    username = models.CharField(unique=True, max_length=255)
    fname = models.CharField(max_length=300, verbose_name="First Name")
    lname = models.CharField(max_length=300, verbose_name="Last Name")
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=360, blank=True)
    class Meta:
        ordering = ('lname','fname')
    
    def save(self, *args, **kwargs):
        super(MdlUser, self).save(*args, **kwargs)
        # create a Django user to match
        user, created = User.objects.get_or_create(username=self.username)
        if user.first_name == "": user.first_name = self.fname
        if user.last_name == "": user.last_name = self.lname
        if user.email == "": user.email = self.email
        if user.password == "": user.password = "!"
        user.save()
        
    def __unicode__(self):
        return self.lname + ", " + self.fname
    
    @property
    def deleted(self):
        # For backwards compatibility
        logger.WARNING('Depreciated use of MdlUser.deleted which was changed to inactive')
        return self.inactive
        
        
    def django_user(self):
        return User.objects.get(username=self.username)
        
    def promote_to_sis(self):
        """ Promote student object to a student worker keeping all fields, does nothing on duplicate. """
        try:
            cursor = connection.cursor()
            cursor.execute("insert into sis_student (mdluser_ptr_id) values (" + str(self.id) + ");")
        except:
            return
            
    def promote_to_faculty(self):
        """ Promote student object to a facultu keeping all fields, does nothing on duplicate. """
        try:
            cursor = connection.cursor()
            cursor.execute("insert into sis_faculty (mdluser_ptr_id) values (" + str(self.id) + ");")
        except:
            return
        
        
        
########################################################################


class PhoneNumber(models.Model):
    number = PhoneNumberField()
    ext = models.CharField(max_length=10, blank=True, null=True)
    type = models.CharField(max_length=2, choices=(('H', 'Home'), ('C', 'Cell'), ('W', 'Work'), ('O', 'Other')), blank=True)
    class Meta:
        abstract = True
    def full_number(self):
        if self.ext:
            return self.number + " x" + self.ext
        else:
            return self.number
            

class EmergencyContact(models.Model):
    fname = models.CharField(max_length=255, verbose_name="First Name")
    mname = models.CharField(max_length=255, blank=True, null=True, verbose_name="Middle Name")
    lname = models.CharField(max_length=255, verbose_name="Last Name")
    relationship_to_student = models.CharField(max_length=500, blank=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = USStateField(blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    primary_contact = models.BooleanField(default=True)
    emergency_only = models.BooleanField(help_text="Only contact in case of emergency")
    
    class Meta:
        ordering = ('primary_contact', 'emergency_only', 'lname') 
        verbose_name = "Student Contact"  
    
    def __unicode__(self):
        txt = self.fname + " " + self.lname
        for number in self.emergencycontactnumber_set.all():
            txt += " " + unicode(number)
        return txt
    
    def save(self, *args, **kwargs):
        super(EmergencyContact, self).save(*args, **kwargs)
        self.cache_student_addresses()
    
    def cache_student_addresses(self):
        """cache these for the student for primary contact only"""
        if self.primary_contact:
            for student in self.student_set.all():
                student.parent_guardian = self.fname + " " + self.lname
                student.city = self.city
                student.street = self.street
                student.state = self.state
                student.zip = self.zip
                student.parent_email = self.email
                student.save()
                for contact in student.emergency_contacts.exclude(id=self.id):
                    # There should only be one primary contact!
                    if contact.primary_contact:
                        contact.primary_contact = False
                        contact.save()
            # cache these for the applicant
            if hasattr(self, 'applicant_set'):
                for applicant in self.applicant_set.all():
                    applicant.set_cache(self)


class EmergencyContactNumber(PhoneNumber):
    contact = models.ForeignKey(EmergencyContact)
    def __unicode__(self):
        if self.ext:
            return self.get_type_display() + ":" + self.number + "x" + self.ext
        else:
            return self.get_type_display() + ":" + self.number


class Faculty(MdlUser):
    alt_email = models.EmailField(blank=True)
    number = PhoneNumberField(blank=True)
    ext = models.CharField(max_length=10, blank=True, null=True)
    teacher = models.BooleanField()
    
    class Meta:
        verbose_name_plural = "Faculty"
        ordering = ("lname", "fname")
    
    def save(self, *args, **kwargs):
        super(Faculty, self).save(*args, **kwargs)
        user, created = User.objects.get_or_create(username=self.username)
        group, created = Group.objects.get_or_create(name="faculty")
        if created: group.save()
        user.groups.add(group)
        user.save()


class Cohort(models.Model):
    name = models.CharField(max_length=255)
    students = models.ManyToManyField('Student', blank=True, null=True, db_table="sis_studentcohort")
    
    def __unicode__(self):
        return unicode(self.name)
    

class ReasonLeft(models.Model):
    reason = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self):
        return unicode(self.reason)


class GradeLevel(models.Model):
    id = models.IntegerField(unique=True, primary_key=True, verbose_name="Grade")
    name = models.CharField(max_length=150, unique=True)
    
    class Meta:
        ordering = ('id',)
    
    def __unicode__(self):
        return unicode(self.name)
        
    @property
    def grade(self):
        return self.id

class LanguageChoice(models.Model):
    name = models.CharField(unique=True, max_length=255)
    iso_code = models.CharField(blank=True, max_length=2, help_text="ISO 639-1 Language code http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes")
    default = models.BooleanField()
    def __unicode__(self):
        return unicode(self.name)
    
    def save(self, *args, **kwargs):
        if self.default:
            for language in LanguageChoice.objects.filter(default=True):
                language.default = False
                language.save()
        super(LanguageChoice, self).save(*args, **kwargs)

def get_default_language():
    if LanguageChoice.objects.filter(default=True).count():
        return LanguageChoice.objects.filter(default=True)[0]
class Student(MdlUser):
    """student based on a Moodle user"""
    mname = models.CharField(max_length=150, blank=True, null=True, verbose_name="Middle Name")
    grad_date = models.DateField(blank=True, null=True)
    pic = ImageWithThumbsField(upload_to="student_pics", blank=True, sizes=((70,65),(530, 400)))
    alert = models.CharField(max_length=500, blank=True, help_text="Warn any user who accesses this record with this text")
    sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), blank=True, null=True)
    bday = models.DateField(blank=True, null=True, verbose_name="Birth Date")
    year = models.ForeignKey(GradeLevel, blank=True, null=True)
    reason_left = models.ForeignKey(ReasonLeft, blank=True, null=True)
    date_dismissed = models.DateField(blank=True, null=True)
    unique_id = models.IntegerField(blank=True, null=True, unique=True)
    ssn = models.CharField(max_length=11, blank=True, null=True)
    
    # These fields are cached from emergency contacts
    parent_guardian = models.CharField(max_length=150, blank=True, editable=False)
    street = models.CharField(max_length=150, blank=True, editable=False)
    state = USStateField(blank=True, editable=False)
    zip = models.CharField(max_length=10, blank=True, editable=False)
    parent_email = models.EmailField(blank=True, editable=False)
    
    family_preferred_language = models.ForeignKey(LanguageChoice, blank=True, null=True, default=get_default_language)
    alt_email = models.EmailField(blank=True, help_text="Alternative student email that is not their school email.")
    notes = models.TextField(blank=True)
    emergency_contacts = models.ManyToManyField(EmergencyContact, blank=True)
    siblings = models.ManyToManyField('Student', blank=True)
    cohorts = models.ManyToManyField(Cohort, through='StudentCohort', blank=True)
    cache_cohort = models.ForeignKey(Cohort, editable=False, blank=True, null=True, help_text="Cached primary cohort.", related_name="cache_cohorts")
    individual_education_program = models.BooleanField()
    cache_gpa = models.DecimalField(editable=False, max_digits=5, decimal_places=2, blank=True, null=True)
    
    class Meta:
        permissions = (
            ("view_student", "View student"),
            ("view_ssn_student", "View student ssn"),
            ("view_mentor_student", "View mentoring information student"),
            ("reports", "View reports"),
        )
    
    def __unicode__(self):
        return self.lname + ", " + self.fname
    
    @property
    def primary_cohort(self):
        return self.cache_cohort
    
    @property
    def phone(self):
        try:
            parent = self.emergency_contacts.order_by('primary_contact')[0]
            return parent.emergencycontactnumber_set.all()[0].number
        except:
            return None
    
    @property
    def he_she(self):
        """ returns "he" or "she" """
        return self.gender_to_word("he", "she")
    
    @property
    def homeroom(self):
        """ Returns homeroom for student """
        from schedule.models import Course
        try:
            courses = self.course_set.filter(homeroom=True)
            homeroom = self.course_set.get( homeroom=True)
        except:
            return ""
    
    @property
    def son_daughter(self):
        """ returns "son" or "daughter" """
        return self.gender_to_word("son", "daughter")
    
    def __calculate_grade_for_courses(self, courses, marking_period=None, date_report=None):
        gpa = float(0)
        credits = float(0)
        for course in courses.distinct():
            try:
                grade = None
                credit = None
                if marking_period:
                    grade = float(self.grade_set.get(course=course, final=True, override_final=False, marking_period=marking_period).get_grade())
                    credit = float(course.credits) / float(course.marking_period.count())
                else:
                    grade = float(course.get_final_grade(self, date_report=date_report)) # don't add in case credits throws ex
                    credit = float(course.get_credits_earned(date_report=date_report))
                # commit
                credits += credit
                gpa += float(grade) * credit
            except:
                pass
        if credits > 0:
            gpa = Decimal(str(gpa/credits)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        else:
            gpa = "N/A"
        return gpa
        
    def calculate_gpa(self, date_report=None):
        """ Calculate students gpa
        date_report: Date for calculation (which effects credit value) defaults to today """
        if date_report == None:
            date_report = date.today()
        courses = self.course_set.filter(graded=True, marking_period__show_reports=True).exclude(omitcoursegpa__student=self).exclude(marking_period__school_year__omityeargpa__student=self).distinct()
        return self.__calculate_grade_for_courses(courses, date_report=date_report)
        
    
    def calculate_gpa_year(self, year=None, date_report=None):
        """ Calculate students gpa for one year
        year: Defaults to active year.
        date_report: Date for calculation (which effects credit value) defaults to today """
        if not date_report:
            date_report = date.today()
        courses = self.course_set.filter(graded=True, marking_period__school_year=year)
        x = self.__calculate_grade_for_courses(courses, date_report=date_report)
        return x
    
    def calculate_gpa_mp(self, marking_period):
        """ Calculate students gpa for one marking periods
        mp: Marking Periods to calculate for."""
        courses = self.course_set.filter(graded=True, omitcoursegpa=None, marking_period=marking_period)
        return self.__calculate_grade_for_courses(courses, marking_period=marking_period)
        
    @property
    def gpa(self):
        """ returns current GPA including absolute latest grades """
        if not self.cache_gpa:
            gpa = self.calculate_gpa()
            if gpa == "N/A":
                return gpa
            else:
                self.cache_gpa = gpa
                self.save()
        return self.cache_gpa
        
    def gender_to_word(self, male_word, female_word):
        """ returns a string based on the sex of student """
        if self.sex == "M":
            return male_word
        elif self.sex == "F":
            return female_word
        else:
            return male_word + "/" + female_word
    
    def cache_cohorts(self):
        cohorts = StudentCohort.objects.filter(student=self)
        if cohorts.filter(primary=True).count():
            self.cache_cohort = cohorts.filter(primary=True)[0].cohort
        elif cohorts.count():
            self.cache_cohort = cohorts[0].cohort
        else:
            self.cache_cohort = None
    
    def save(self, *args, **kwargs):
        self.cache_cohorts()
        super(Student, self).save(*args, **kwargs)
        user, created = User.objects.get_or_create(username=self.username)
        group, gcreated = Group.objects.get_or_create(name="students")
        user.groups.add(group)
        
    def graduate_and_create_alumni(self):
        self.inactive = True
        self.reason_left = ReasonLeft.objects.get_or_create(reason="Graduated")[0]
        if 'ecwsp.alumni' in settings.INSTALLED_APPS:
            from ecwsp.alumni.models import Alumni
            Alumni.objects.get_or_create(student=self)
        self.save()
    
    def promote_to_worker(self):
        """ Promote student object to a student worker keeping all fields, does nothing on duplicate. """
        try:
            cursor = connection.cursor()
            cursor.execute("insert into work_study_studentworker (student_ptr_id, fax) values (" + str(self.id) + ", 0);")
        except:
            return
    
    def get_disciplines(self):
        return self.studentdiscipline_set.all()

class ASPHistory(models.Model):
    student = models.ForeignKey(Student)
    asp = models.CharField(max_length=255)
    date = models.DateField(default=date.today)
    enroll = models.BooleanField(help_text="Check if enrollment, uncheck if unenrollment")
    
    def __unicode__(self):
        if self.enroll:
            return '%s enrolled in %s on %s' % (unicode(self.student), unicode(self.asp), self.date)
        else:
            return '%s left %s on %s' % (unicode(self.student), unicode(self.asp), self.date)

class StudentCohort(models.Model):
    student = models.ForeignKey(Student)
    cohort = models.ForeignKey(Cohort)
    primary = models.BooleanField()
    
    class Meta:
        managed = False
    
    def save(self, *args, **kwargs):
        if self.primary:
            for cohort in StudentCohort.objects.filter(student=self.student).exclude(id=self.id):
                cohort.primary = False
                cohort.save()
                
        super(StudentCohort, self).save(*args, **kwargs)
        
        if self.primary:
            self.student.cache_cohort = self.cohort
            self.student.save()


class TranscriptNoteChoices(models.Model):
    """Returns a predefined transcript note.
    When displayed from "TranscriptNote":
    Replaces $student with student name
    Replaces $he_she with student's appropriate gender word.
    """
    note = models.TextField()
    def __unicode__(self):
        return unicode(self.note)


class TranscriptNote(models.Model):
    """ These are notes intended to be shown on a transcript. They may be either free
    text or a predefined choice. If both are entered they will be concatenated.
    """
    note = models.TextField(blank=True)
    predefined_note = models.ForeignKey(TranscriptNoteChoices, blank=True, null=True)
    student = models.ForeignKey(Student)
    def __unicode__(self):
        note = unicode(self.predefined_note)
        note = note.replace('$student', unicode(self.student))
        note = note.replace('$he_she', self.student.he_she)
        if self.note:
            return unicode(self.note) + " " + unicode(note)
        else:
            return unicode(note)


class StudentNumber(PhoneNumber):
    student = models.ForeignKey(Student, blank=True, null=True)
    
    def __unicode__(self):
        return self.number


class StudentFile(models.Model):
    file = models.FileField(upload_to="student_files")
    student = models.ForeignKey(Student)


class StudentHealthRecord(models.Model):
    student = models.ForeignKey(Student)
    record = models.TextField()

    
class PresetComment(models.Model):
    """ A model with a terrible name, it should be infraction"""
    comment = models.CharField(max_length=255, help_text='If comment is "Case note" these infractions will not be counted as a discipline issue in reports')
    
    class Meta:
        verbose_name = "Infraction"
    
    def __unicode__(self):
        if len(self.comment) < 42:
            return self.comment
        else:
            return unicode(self.comment[:42]) + ".."
        
    def all_actions(self):
        ordering = ('comment',)


class DisciplineAction(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self): 
        return unicode(self.name)


class DisciplineActionInstance(models.Model):
    action = models.ForeignKey(DisciplineAction)
    student_discipline = models.ForeignKey('StudentDiscipline')
    quantity = models.IntegerField(default=1)
    def __unicode__(self): 
        return unicode(self.action) + " (" + unicode(self.quantity) + ")"


class StudentDiscipline(models.Model):
    students = models.ManyToManyField(Student, limit_choices_to={'inactive': False})
    date = models.DateField(default=datetime.today)
    infraction = models.ForeignKey(PresetComment, blank=True, null=True)
    action = models.ManyToManyField(DisciplineAction, through='DisciplineActionInstance')
    comments = models.TextField(blank=True)
    teacher = models.ForeignKey(Faculty, blank=True, null=True)
    
    def show_students(self):
        if self.students.count() == 1:
            return self.students.all()[0]
        elif self.students.count() > 1:
            return "Multiple students"
        else:
            return None
    
    def comment_Brief(self):
        return self.comments[:100]
     
    class Meta:
        ordering = ('-date',)
        
    def __unicode__(self):
        if self.students.count() == 1:
            stu = self.students.all()[0]
            return unicode(stu) + " " + unicode(self.date)
        return "Multiple Students " + unicode(self.date)
    
    def all_actions(self):
        action = ""
        for a in self.disciplineactioninstance_set.all():
            action += unicode(a) + " "
        return action
    
    def get_active(self):
        """Returns all active discipline records for the school year. 
        If schedule is not installed it returns all records
        Does not return case notes"""
        try:
            school_start = SchoolYear.objects.get(active_year=True).start_date
            school_end = SchoolYear.objects.get(active_year=True).end_date
            case_note = PresetComment.objects.get(comment="Case note")
            return StudentDiscipline.objects.filter(date__range=(school_start, school_end)).exclude(infraction=case_note)
        except:
            case_note = PresetComment.objects.get(comment="Case note")
            return StudentDiscipline.objects.all().exclude(infraction=case_note)
        

class AttendanceStatus(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text='"Present" will not be saved but may show as a teacher option.')
    code = models.CharField(max_length=10, unique=True, help_text="Short code used on attendance reports. Ex: A might be the code for the name Absent")
    teacher_selectable = models.BooleanField()
    excused = models.BooleanField()
    absent = models.BooleanField(help_text="Some statistics need to add various types of absent statuses, such as the number in parathesis in daily attendance")
    tardy = models.BooleanField(help_text="Some statistics need to add various types of tardy statuses, such as the number in parathesis in daily attendance")
    
    class Meta:
        verbose_name_plural = 'Attendance Statuses'
    
    def __unicode__(self):
        return unicode(self.name)


class StudentAttendance(models.Model):
    student =  models.ForeignKey(Student, limit_choices_to={'inactive': False}, related_name="student_attn", help_text="Start typing a student's first or last name to search")
    date = models.DateField(default=datetime.now)
    status = models.ForeignKey(AttendanceStatus)
    notes = models.CharField(max_length=500, blank=True)
    private_notes = models.CharField(max_length=500, blank=True)
    
    class Meta:
        unique_together = (("student", "date", 'status'),)
        ordering = ('-date', 'student',)
        permissions = (
            ('take_studentattendance', 'Take own student attendance'),
        )
    
    def __unicode__(self):
        return unicode(self.student) + " " + unicode(self.date) + " " + unicode(self.status)
        
    def save(self, *args, **kwargs):
        """Don't save Present """
        present, created = AttendanceStatus.objects.get_or_create(name="Present")
        if self.status != present:
            super(StudentAttendance, self).save(*args, **kwargs)
        else:
            try: self.delete()
            except: pass

class AttendanceLog(models.Model):
    date = models.DateField(default=date.today)
    user = models.ForeignKey(User)
    course = models.ForeignKey('schedule.Course')
    asp = models.BooleanField(help_text="ASP attendance, if unchecked this is for a homeroom")
    def __unicode__(self):
        return unicode(self.user) + " " + unicode(self.date)


class AttendanceDailyStat(models.Model):
    date = models.DateField(auto_now_add=True)
    present = models.IntegerField()
    absent = models.IntegerField()
    tardy = models.IntegerField()
    
    def set_all(self):
        """ Records fields and saves """
        all_students = Student.objects.filter(inactive=False).count()
        absents = StudentAttendance.objects.filter(date=date.today(), status__absent=True).count()
        tardies = StudentAttendance.objects.filter(date=date.today(), status__tardy=True).count()
        
        self.present = all_students - absents
        self.absent = absents
        self.tardy = tardies
        self.save()


class ASPAttendance(models.Model):
    date = models.DateField(auto_now_add=True)
    student = models.ForeignKey(Student)
    status = models.CharField(max_length=1, choices=(('P', 'Present'),('A','Absent'),('E','Excused'),('S','Absent in School'),('D','Dismissed')))
    notes = models.CharField(max_length=1000, blank=True)
    course = models.ForeignKey('schedule.Course', blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return unicode(self.date) + " " + unicode(self.student) + " " + unicode(self.status)


class SchoolYear(models.Model):
    name = models.CharField(max_length=255, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    grad_date = models.DateField(blank=True, null=True)
    active_year = models.BooleanField(help_text="The active year is used for calculations such as student discipline records number of incidents")
    
    class Meta:
        ordering = ('-start_date',)
    
    def __unicode__(self):
        return self.name
    
    def get_number_days(self, date=date.today()):
        """ Returns number of active school days in this year, based on
        each marking period of the year.
        date: Defaults to today, date to count towards. Used to get days up to a certain date"""
        mps = self.markingperiod_set.all().order_by('start_date')
        day = 0
        for mp in mps:
            day += mp.get_number_days(date)
        return day
    
    def save(self, *args, **kwargs):
        if self.active_year:
            all = SchoolYear.objects.exclude(id=self.id).update(active_year=False)
        super(SchoolYear, self).save(*args, **kwargs) 
    
    
