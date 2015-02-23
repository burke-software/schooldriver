from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.db import connection
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from localflavor.us.models import USStateField, PhoneNumberField  #, USSocialSecurityNumberField
from django.contrib.auth.models import User, Group
from django.conf import settings
from constance import config

import logging
from thumbs import ImageWithThumbsField
from datetime import date
from ecwsp.administration.models import Configuration
from custom_field.custom_field import CustomFieldModel
import sys
from ckeditor.fields import RichTextField
from django_cached_field import CachedDecimalField
from decimal import Decimal
from ecwsp.sis.helper_functions import round_as_decimal

logger = logging.getLogger(__name__)


def create_faculty(instance, make_user_group=True):
    """ Create a sis.Faculty object that is linked to the given
    auth_user instance. Important as there is no way to do this
    from Django admin. See
    http://stackoverflow.com/questions/4064808/django-model-inheritance-create-sub-instance-of-existing-instance-downcast
    """
    if not hasattr(instance, "student") and not hasattr(instance, "faculty"):
        faculty = Faculty(user_ptr_id=instance.id)
        faculty.__dict__.update(instance.__dict__)
        faculty.save(make_user_group=make_user_group)

def create_student(instance):
    """ Create a sis.Student object that is linked to the given auth_user
    instance. See create_faculty for more details.
    """
    if not hasattr(instance, "student") and not hasattr(instance, 'faculty'):
        student = Student(user_ptr_id=instance.id)
        student.__dict__.update(instance.__dict__)
        student.save()

def create_faculty_profile(sender, instance, created, **kwargs):
    if instance.groups.filter(name="faculty").count():
        create_faculty(instance, make_user_group=False)
    if instance.groups.filter(name="students").count():
        create_student(instance)

def create_faculty_profile_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add' and instance.groups.filter(name="faculty").count():
        create_faculty(instance, make_user_group=False)
    if action == 'post_add' and instance.groups.filter(name="students").count():
        create_student(instance)

post_save.connect(create_faculty_profile, sender=User)
m2m_changed.connect(create_faculty_profile_m2m, sender=User.groups.through)

def get_prefered_format():
    try:
        return config.PREFERED_FORMAT
    except AttributeError:
        return None
class UserPreference(models.Model):
    """ User Preferences """
    file_format_choices = (
        ('o', 'Open Document Format (.odt, .ods)'),
        ('m', 'Microsoft Binary (.doc, .xls)'),
        ('x', 'Microsoft Office Open XML (.docx, .xlsx)'),
    )
    prefered_file_format = models.CharField(verbose_name="Preferred file format", default=get_prefered_format, max_length="1", choices=file_format_choices, help_text="Open Document Format is recommended.")
    include_deleted_students = models.BooleanField(default=False, help_text="When searching for students, include deleted (previous) students.")
    gradebook_preference = models.CharField(max_length=10, blank=True, choices=(
         ('O', 'Online Gradebook'), ('S','Spreadsheet'), ('E', 'Engrade'), ('M', 'Manual')))
    user = models.ForeignKey(User, unique=True, editable=False)
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

class PhoneNumber(models.Model):
    number = PhoneNumberField()
    ext = models.CharField(max_length=10, blank=True, null=True)
    type = models.CharField(max_length=2, choices=(('H', 'Home'), ('C', 'Cell'), ('W', 'Work'), ('O', 'Other')), blank=True)
    note = models.CharField(max_length=255, blank=True)
    class Meta:
        abstract = True
    def full_number(self):
        if self.ext:
            return self.number + " x" + self.ext
        else:
            return self.number


def get_city():
    return Configuration.get_or_default("Default City", "").value
class EmergencyContact(models.Model):
    fname = models.CharField(max_length=255, verbose_name="First Name")
    mname = models.CharField(max_length=255, blank=True, null=True, verbose_name="Middle Name")
    lname = models.CharField(max_length=255, verbose_name="Last Name")
    relationship_to_student = models.CharField(max_length=500, blank=True)
    street = models.CharField(max_length=255, blank=True, null=True, help_text="Include apt number")
    city = models.CharField(max_length=255, blank=True, null=True, default=get_city)
    state = USStateField(blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(blank=True)
    primary_contact = models.BooleanField(default=True, help_text="This contact is where mailings should be sent to. In the event of an emergency, this is the person that will be contacted first.")
    emergency_only = models.BooleanField(default=False, help_text="Only contact in case of emergency")
    sync_schoolreach = models.BooleanField(help_text="Sync this contact with schoolreach",default=True)

    class Meta:
        ordering = ('primary_contact', 'lname')
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
        """cache these for the student for primary contact only
        There is another check on Student in case all contacts where deleted"""
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

    def show_student(self):
        students = ""
        for student in self.student_set.all():
            students += "{}, ".format(student)
        return students[:-2]

class EmergencyContactNumber(PhoneNumber):
    contact = models.ForeignKey(EmergencyContact)
    primary = models.BooleanField(default=False, )

    class Meta:
        verbose_name = "Student Contact Number"

    def save(self, *args, **kwargs):
        if self.primary:
            for contact in self.contact.emergencycontactnumber_set.exclude(id=self.id).filter(primary=True):
                contact.primary = False
                contact.save()
        super(EmergencyContactNumber, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.ext:
            return self.get_type_display() + ":" + self.number + "x" + self.ext
        else:
            return self.get_type_display() + ":" + self.number


class Faculty(User):
    number = PhoneNumberField(blank=True)
    ext = models.CharField(max_length=10, blank=True, null=True)
    teacher = models.BooleanField(default=False, )

    class Meta:
        verbose_name_plural = "Faculty"
        ordering = ("last_name", "first_name")

    def save(self, make_user_group=True, *args, **kwargs):
        self.is_staff = True
        super(Faculty, self).save(*args, **kwargs)
        if make_user_group:
            group, created = Group.objects.get_or_create(name="faculty")
            self.groups.add(group)

    def __unicode__(self):
        if self.last_name:
            return u"{0}, {1}".format(self.last_name, self.first_name)
        return self.username


class Cohort(models.Model):
    name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=500, blank=True, help_text="Optional verbose name")
    students = models.ManyToManyField('Student', blank=True, through='StudentCohort')
    primary = models.BooleanField(default=False, help_text="If set true - all students in this cohort will have it set as primary!")

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


@receiver(post_save, sender=Cohort)
def after_cohort_m2m(sender, instance, **kwargs):
    if instance.primary:
        for student in instance.students.all():
            student_cohort = student.studentcohort_set.filter(cohort__id=instance.id).first()
            student_cohort.primary = True
            student_cohort.save()


class PerCourseSectionCohort(Cohort):
    course_section = models.ForeignKey('schedule.CourseSection')


class ReasonLeft(models.Model):
    reason = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return unicode(self.reason)


class GradeLevel(models.Model):
    id = models.IntegerField(unique=True, primary_key=True, verbose_name="Grade Number")
    name = models.CharField(max_length=150, unique=True, verbose_name="Grade Name")

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
    default = models.BooleanField(default=False, )
    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        if self.default:
            for language in LanguageChoice.objects.filter(default=True):
                language.default = False
                language.save()
        super(LanguageChoice, self).save(*args, **kwargs)

class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)
    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)

class ClassYear(models.Model):
    """ Class year such as class of 2010.
    """
    year = IntegerRangeField(unique=True, min_value=1900, max_value=2200, help_text="Example 2014")
    full_name = models.CharField(max_length=255, help_text="Example Class of 2014", blank=True)

    class Meta:
        verbose_name = "Graduating Class"
        verbose_name_plural = "Graduating Classes"

    def __unicode__(self):
        return unicode(self.full_name)

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = "Class of %s" % (self.year,)
        super(ClassYear, self).save(*args, **kwargs)


def get_default_language():
    if LanguageChoice.objects.filter(default=True).count():
        return LanguageChoice.objects.filter(default=True)[0]


if settings.MIGRATIONS_DISABLED is True:
    family_ref = 'auth.User'
else:
    family_ref = 'FamilyAccessUser'

class Student(User, CustomFieldModel):
    mname = models.CharField(max_length=150, blank=True, null=True, verbose_name="Middle Name")
    grad_date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    pic = ImageWithThumbsField(upload_to="student_pics", blank=True, null=True, sizes=((70,65),(530, 400)))
    alert = models.CharField(max_length=500, blank=True, help_text="Warn any user who accesses this record with this text")
    sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), blank=True, null=True)
    bday = models.DateField(blank=True, null=True, verbose_name="Birth Date", validators=settings.DATE_VALIDATORS)
    year = models.ForeignKey(
        GradeLevel,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Grade level")
    class_of_year = models.ForeignKey(ClassYear, verbose_name="Graduating Class", blank=True, null=True)
    date_dismissed = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    reason_left = models.ForeignKey(ReasonLeft, blank=True, null=True)
    unique_id = models.IntegerField(blank=True, null=True, unique=True, help_text="For integration with outside databases")
    ssn = models.CharField(max_length=11, blank=True, null=True)  #Once 1.1 is out USSocialSecurityNumberField(blank=True)

    # These fields are cached from emergency contacts
    parent_guardian = models.CharField(max_length=150, blank=True, editable=False)
    street = models.CharField(max_length=150, blank=True, editable=False)
    state = USStateField(blank=True, editable=False, null=True)
    city = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=10, blank=True, editable=False)
    parent_email = models.EmailField(blank=True, editable=False)

    family_preferred_language = models.ForeignKey(LanguageChoice, blank=True, null=True, default=get_default_language)
    family_access_users = models.ManyToManyField(
        family_ref,
        blank=True,
        related_name="+",
    )
    alt_email = models.EmailField(blank=True, help_text="Alternative student email that is not their school email.")
    notes = models.TextField(blank=True)
    emergency_contacts = models.ManyToManyField(EmergencyContact, verbose_name="Student Contact", blank=True)
    siblings = models.ManyToManyField('Student', blank=True)
    cohorts = models.ManyToManyField(Cohort, through='StudentCohort', blank=True)
    cache_cohort = models.ForeignKey(Cohort, editable=False, blank=True, null=True, on_delete=models.SET_NULL, help_text="Cached primary cohort.", related_name="cache_cohorts")
    individual_education_program = models.BooleanField(default=False)
    gpa = CachedDecimalField(editable=False, max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        permissions = (
            ("view_student", "View student"),
            ("view_ssn_student", "View student ssn"),
            ("view_mentor_student", "View mentoring information student"),
            ("reports", "View reports"),
        )
        ordering = ("last_name", "first_name")

    def __unicode__(self):
        return u"{0}, {1}".format(self.last_name, self.first_name)

    def get_absolute_url():
        pass

    # TC requested this for transcript template
    def get_long_grad_date(self):
        return self.grad_date.strftime('%B %d, %Y')

    def get_gpa(self, rounding=2, numeric_scale=False, boost=True):
        """ Get cached gpa but with rounding and scale options """
        gpa = self.gpa

        if numeric_scale == True:
            # Get the scale for the last year the student was active in
            grade_scale = GradeScale.objects.filter(
                schoolyear__markingperiod__coursesection__courseenrollment__user=self).last()
            if grade_scale:
                gpa = grade_scale.to_numeric(gpa)
                enrollments = self.courseenrollment_set.filter(
                        course_section__course__course_type__weight__gt=0)
                if boost:
                    boost_sum = enrollments.aggregate(boost_sum=Sum('course_section__course__course_type__boost'))['boost_sum']
                    boost_factor = boost_sum /  enrollments.count()
                    gpa += boost_factor
        if rounding:
            gpa = round_as_decimal(gpa, rounding)
        return gpa

    def calculate_gpa(self, date_report=None, rounding=2, prescale=False, boost=True):
        """ Use StudentYearGrade calculation
        No further weighting needed.
        """
        total = Decimal(0)
        years_with_grade = 0
        grade_years = self.studentyeargrade_set.filter(year__markingperiod__show_reports=True)
        if date_report:
            grade_years = grade_years.filter(year__start_date__lt=date_report)
        for grade_year in grade_years.distinct():

            # grade = grade_year.calculate_grade(date_report=date_report, prescale=prescale)

            grade = grade_year.get_grade(
                date_report = date_report,
                numeric_scale = True,
                rounding = rounding,
                prescale = prescale,
                boost = boost
                )
            if grade:
                # Is this an incomplete complete year?
                if date_report and date_report < grade_year.year.end_date:
                    # This year hasn't finished. What fraction is complete?
                    all_mps = grade_year.year.markingperiod_set.count()
                    complete_mps = grade_year.year.markingperiod_set.filter(
                        end_date__lte=date_report).count()
                    fraction = Decimal(complete_mps) / all_mps
                    total += grade * grade_year.credits * fraction
                    years_with_grade += grade_year.credits * fraction
                else:
                    total += grade * grade_year.credits
                    years_with_grade += grade_year.credits

        if years_with_grade:
            gpa = total / years_with_grade
            return round_as_decimal(gpa, decimal_places=rounding)

    @property
    def primary_cohort(self):
        return self.cache_cohort

    @property
    def phone(self):
        try:
            parent = self.emergency_contacts.order_by('-primary_contact')[0]
            return parent.emergencycontactnumber_set.all()[0].number
        except IndexError:
            return None

    @property
    def he_she(self):
        """ returns "he" or "she" """
        return self.gender_to_word("he", "she")

    @property
    def homeroom(self):
        """ Returns homeroom for student """
        from schedule.models import CourseSection
        try:
            courses = self.coursesection_set.filter(course__homeroom=True)
            homeroom = self.coursesection_set.get(course__homeroom=True)
        except:
            return ""

    @property
    def son_daughter(self):
        """ returns "son" or "daughter" """
        return self.gender_to_word("son", "daughter")

    @property
    def get_email(self):
        """ Returns email address using various configurable methods """
        email_method = Configuration.get_or_default(
            "How to obtain student email",
            default="append",
            help_text="append, user, or student.").value
        if email_method == "append":
            email_end = Configuration.get_or_default("email", default="@change.me").value
            return '%s%s' % (self.student.username, email_end)
        elif email_method == "user":
            if User.objects.filter(username=self.student.username):
                return User.objects.filter(username=self.student.username)[0].email
            return None
        return self.alt_email

    def get_phone_number(self):
        if self.studentnumber_set.filter(type="C"):
            return self.studentnumber_set.filter(type="C")[0]
        elif self.studentnumber_set.all():
            return self.studentnumber_set.all()[0]

    def get_primary_emergency_contact(self):
        if self.emergency_contacts.filter(primary_contact=True):
            return self.emergency_contacts.filter(primary_contact=True)[0]

    def get_disciplines(self, mps, action_name=None, count=True):
        """ Shortcut to look up discipline records
        mp: Marking Period
        action_name: Discipline action name
        count: Boolean - Just the count of them """
        if hasattr(mps,'db'): # More than one?
            if len(mps):
                start_date = mps.order_by('start_date')[0].start_date
                end_date = mps.order_by('-end_date')[0].end_date
                disc = self.studentdiscipline_set.filter(date__range=(start_date,end_date))
            else:
                disc = self.studentdiscipline_set.none()
        else:
            disc = self.studentdiscipline_set.filter(date__range=(mps.start_date,mps.end_date))
        if action_name:
            disc = disc.filter(action__name=action_name)
        if count:
            return disc.count()
        else:
            return disc

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

    def get_year(self, active_year):
        """ get the year (fresh, etc) from the class of XX year.
        """
        if self.class_of_year:
            try:
                this_year = active_year.end_date.year
                school_last_year = GradeLevel.objects.order_by('-id')[0].id
                class_of_year = self.class_of_year.year

                target_year = school_last_year - (class_of_year - this_year)
                return GradeLevel.objects.get(id=target_year)
            except:
                return None

    def get_scaled_multiple_mp_average_by_indices(self, indices, rounding=2):
        """ Get a scaled mulitple marking period average for this student
        Requires that the property mps be set previously.
        This function exists mainly for appy based report cards where speed,
        and simplicity (in the template) are important.
        """
        from ecwsp.grades.models import Grade
        mps = [ self.mps[i] for i in indices ]
        return Grade.get_scaled_multiple_mp_average(self, mps, rounding)


    def determine_year(self):
        """ Set the year (fresh, etc) from the class of XX year.
        """
        if self.class_of_year:
            try:
                active_year = SchoolYear.objects.filter(active_year=True)[0]
                self.year = self.get_year(active_year)
            except:
                return None

    def save(self, creating_worker=False, *args, **kwargs):
        self.cache_cohorts()
        if self.is_active == False and (Configuration.get_or_default("Clear Placement for Inactive Students","False").value == "True" \
        or Configuration.get_or_default("Clear Placement for Inactive Students","False").value == "true" \
        or Configuration.get_or_default("Clear Placement for Inactive Students","False").value == "T"):
            try:
                self.studentworker.placement = None
                self.studentworker.save()
            except: pass
        # Check year
        self.determine_year()
        super(Student, self).save(*args, **kwargs)

        # Create student worker if the app is installed.
        # https://code.djangoproject.com/ticket/7623
        if 'ecwsp.work_study' in settings.INSTALLED_APPS:
            if not creating_worker and not hasattr(self, 'studentworker'):
                from ecwsp.work_study.models import StudentWorker
                worker = StudentWorker(user_ptr_id=self.user_ptr_id)
                worker.__dict__.update(self.__dict__)
                worker.save(creating_worker=True)

        group, gcreated = Group.objects.get_or_create(name="students")
        self.user_ptr.groups.add(group)


    def clean(self, *args, **kwargs):
        """ Check if a Faculty exists, can't have someone be a Student and Faculty """
        if Faculty.objects.filter(id=self.id).count():
            raise ValidationError('Cannot have someone be a student AND faculty!')
        super(Student, self).clean(*args, **kwargs)

    def graduate_and_create_alumni(self):
        self.inactive = True
        self.reason_left = ReasonLeft.objects.get_or_create(reason="Graduated")[0]
        if not self.grad_date:
            self.grad_date = date.today()
        if 'ecwsp.alumni' in settings.INSTALLED_APPS:
            from ecwsp.alumni.models import Alumni
            Alumni.objects.get_or_create(student=self)
        self.save()

    def promote_to_worker(self):
        """ Promote student object to a student worker keeping all fields, does nothing on duplicate. """
        try:
            cursor = connection.cursor()
            cursor.execute("insert into work_study_studentworker (student_ptr_id) values (" + str(self.id) + ");")
        except:
            return
def after_student_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if hasattr(instance, 'emergency_contacts'): # Apparently instance might be whatever the fuck it wants to be, not just student.
        if not instance.emergency_contacts.filter(primary_contact=True).count():
            # No contacts, set cache to None
            instance.parent_guardian = ""
            instance.city = ""
            instance.street = ""
            instance.state = ""
            instance.zip = ""
            instance.parent_email = ""
            instance.save()
        for ec in instance.emergency_contacts.filter(primary_contact=True):
            ec.cache_student_addresses()


m2m_changed.connect(after_student_m2m, sender=Student.emergency_contacts.through)


class StudentCohort(models.Model):
    student = models.ForeignKey(Student)
    cohort = models.ForeignKey(Cohort)
    primary = models.BooleanField(default=False, )

    #class Meta:
    #    auto_created = Student

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


class GradeScale(models.Model):
    """ Translate a numeric grade to some other scale.
    Example: Letter grade or 4.0 scale. """
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return '{}'.format(self.name)

    def get_rule(self, grade):
        if grade is not None:
            return self.gradescalerule_set.filter(min_grade__lte=grade, max_grade__gte=grade).first()

    def to_letter(self, grade):
        rule = self.get_rule(grade)
        if rule:
            return rule.letter_grade

    def to_numeric(self, grade):
        rule = self.get_rule(grade)
        if rule:
            return rule.numeric_scale


class GradeScaleRule(models.Model):
    """ One rule for a grade scale.  """
    min_grade = models.DecimalField(max_digits=5, decimal_places=2)
    max_grade = models.DecimalField(max_digits=5, decimal_places=2)
    letter_grade = models.CharField(max_length=50, blank=True)
    numeric_scale = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    grade_scale = models.ForeignKey(GradeScale)

    class Meta:
        unique_together = ('min_grade', 'max_grade', 'grade_scale')

    def __unicode__(self):
        return '{}-{} {} {}'.format(self.min_grade, self.max_grade, self.letter_grade, self.numeric_scale)


def get_default_benchmark_grade():
    return str(Configuration.get_or_default("Benchmark-based grading", "False").value).lower() == "true"

class SchoolYear(models.Model):
    name = models.CharField(max_length=255, unique=True)
    start_date = models.DateField(validators=settings.DATE_VALIDATORS)
    end_date = models.DateField(validators=settings.DATE_VALIDATORS)
    grad_date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    grade_scale = models.ForeignKey(GradeScale, blank=True, null=True, help_text="Alternative grade scale such as letter grades or a 4.0 scale")
    active_year = models.BooleanField(default=False,
        help_text="DANGER!! This is the current school year. There can only be one and setting this will remove it from other years. " \
                  "If you want to change the active year you almost certainly want to click Management, Change School Year.")
    benchmark_grade = models.BooleanField(default=get_default_benchmark_grade,
                                          help_text="Causes additional information to appear on transcripts. The configuration option \"Benchmark-based grading\" sets the default for this field.")

    class Meta:
        ordering = ('-start_date',)

    def __unicode__(self):
        return self.name

    def get_number_days(self, date=date.today()):
        """ Returns number of active school days in this year, based on
        each marking period of the year.
        date: Defaults to today, date to count towards. Used to get days up to a certain date"""
        mps = self.markingperiod_set.filter(show_reports=True).order_by('start_date')
        day = 0
        for mp in mps:
            day += mp.get_number_days(date)
        return day

    def save(self, *args, **kwargs):
        super(SchoolYear, self).save(*args, **kwargs)
        if self.active_year:
            all = SchoolYear.objects.exclude(id=self.id).update(active_year=False)


class MessageToStudent(models.Model):
    """ Stores a message to be shown to students for a specific amount of time
    """
    message = RichTextField(help_text="This message will be shown to students when they log in.")
    start_date = models.DateField(default=date.today, validators=settings.DATE_VALIDATORS)
    end_date = models.DateField(default=date.today, validators=settings.DATE_VALIDATORS)
    def __unicode__(self):
        return self.message


class FamilyAccessUser(User):
    """ A person who can log into the non-admin side and see the same view as a student,
    except that he/she cannot submit timecards.
    This proxy model allows non-superuser registrars to update family user accounts.
    """
    class Meta:
        proxy = True
        ordering = ("last_name", "first_name")
    def __unicode__(self):
        return u"{0}".format(self.username)
    def save(self, *args, **kwargs):
        super(FamilyAccessUser, self).save(*args, **kwargs)
        self.groups.add(Group.objects.get_or_create(name='family')[0])
