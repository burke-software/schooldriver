from django.db import models
from django.db import IntegrityError
from localflavor.us.models import USStateField, PhoneNumberField
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.safestring import mark_safe

from ckeditor.fields import RichTextField
from ecwsp.sis.models import Student

import datetime

program_years_choices = (
    ('4', '4-year or higher institution'),
    ('2', '2-year institution'),
    ('L', 'less than 2-year institution'),  
)

class College(models.Model):
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    state = USStateField(blank=True)
    type = models.CharField(max_length=60, choices=(('Public','Public'),('Private','Private')), blank=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ['name']

class CollegeEnrollment(models.Model):
    """ Mostly a place to keep Student clearinghouse enrollment data """
    search_date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    college = models.ForeignKey(College)
    program_years = models.CharField(max_length=1, choices=program_years_choices, blank=True, null=True)
    begin = models.DateField(blank=True,null=True, validators=settings.DATE_VALIDATORS)
    end = models.DateField(blank=True,null=True, validators=settings.DATE_VALIDATORS)
    status_choices = (
        ('F', 'Full-time'),
        ('H', 'Half-time'),
        ('L', 'Less than half-time'),
        ('A', 'Leave of absence'),
        ('W', 'Withdrawn'),
        ('D', 'Deceased'),
    )
    status = models.CharField(max_length=1, choices=status_choices, blank=True,null=True)
    graduated = models.BooleanField(default=False, )
    graduation_date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    degree_title = models.CharField(max_length=255, blank=True, null=True)
    major = models.CharField(max_length=255, blank=True, null=True)
    alumni = models.ForeignKey('Alumni')
    college_sequence = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return unicode(self.college)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Don't allow draft entries to have a pub_date.
        if self.begin > self.end:
            raise ValidationError('Cannot end before beginning.')
    
    def save(self, *args, **kwargs):
        super(CollegeEnrollment, self).save(*args, **kwargs)
        # Cache these in the database
        self.alumni.handle_cache()

class AlumniStatus(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        verbose_name_plural = "Alumni Statuses"
        ordering = ['name']

class Withdrawl(models.Model):
    college = models.ForeignKey(College)
    alumni = models.ForeignKey('Alumni')
    date = models.DateField(default=datetime.date.today, validators=settings.DATE_VALIDATORS)
    semesters = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=3, help_text="Number of semesters/trimesters at this college.")
    from_enrollment = models.BooleanField(default=False, )
    
    def __unicode__(self):
        return "%s left %s on %s" % (self.alumni, self.college, self.date)

class AlumniNoteCategory(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return unicode(self.name)

class AlumniNote(models.Model):
    category = models.ForeignKey(AlumniNoteCategory, blank=True, null=True)
    note = RichTextField()
    alumni = models.ForeignKey('Alumni')
    date = models.DateField(auto_now_add=True, validators=settings.DATE_VALIDATORS)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    
    def get_note(self):
        return mark_safe(self.note)
    
    
    def __unicode__(self):
        return "%s %s: %s" % (self.user, self.date, self.note)

class AlumniAction(models.Model):
    title = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    alumni = models.ManyToManyField('Alumni', blank=True, null=True)
    date = models.DateField(default=datetime.date.today, blank=True, null=True, validators=settings.DATE_VALIDATORS)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    
    def __unicode__(self):
        return "%s %s" % (self.title, self.date)

class AlumniEmail(models.Model):
    email = models.EmailField()
    type = models.CharField(
        max_length=255,
        choices=(('Personal', 'Personal'), ('School', 'School'), ('Work', 'Work'), ('Other', 'Other')),
        blank=True,
        null=True,
        )
    alumni = models.ForeignKey('Alumni')
    def __unicode__(self):
        return self.email
class AlumniPhoneNumber(models.Model):
    phone_number = PhoneNumberField()
    type = models.CharField(
        max_length=255,
        choices=(('H', 'Home'), ('C', 'Cell'), ('W', 'Work'), ('O', 'Other')),
        blank=True,
        null=True,
        )
    alumni = models.ForeignKey('Alumni')
    def __unicode__(self):
        return self.phone_number

class Alumni(models.Model):
    student = models.OneToOneField(Student, unique=True)
    college = models.ForeignKey(College, blank=True, null=True, related_name="college_student")
    graduated = models.BooleanField(default=False, )
    graduation_date = models.DateField(blank=True, null=True, help_text="Expected or actual graduation date", validators=settings.DATE_VALIDATORS)
    college_override = models.BooleanField(default=False, 
        help_text="If checked, college enrollment data will not set college and graduated automatically.")  
    status = models.ForeignKey(AlumniStatus, blank=True, null=True)
    program_years = models.CharField(max_length=1, choices=program_years_choices, blank=True, null=True)
    semesters = models.CharField(max_length="5", blank=True, help_text="Number of semesters or trimesters.")
    withdrawls = models.ManyToManyField(College, through=Withdrawl)
    on_track = models.BooleanField(default=False, help_text="On track to graduate")
    
    class Meta:
        verbose_name_plural = "Alumni"
    
    def __unicode__(self):
        return unicode(self.student)
    
    def save(self, *args, **kwargs):
        if id:
            new = False
        else:
            new = True
        super(Alumni, self).save(*args, **kwargs)
        if new and self.student:
            # copy old data, we want to keep it for archieval reasons
            if self.student.alt_email:
                AlumniEmail.create(email=self.student.alt_email,type="Imported Alt Email",alumni=self)
            if self.student.email:
                AlumniEmail.create(email=self.student.alt_email,type="Imported Email",alumni=self)
            for number in self.student.studentnumber_set.all():
                AlumniPhoneNumber.create(phone_number=number.number,type=number.type,alumni=self)
    
    def handle_cache(self):
        """ Sets cache and college unless college_override is checked """
        if not self.college_override:
            last_enroll = self.collegeenrollment_set.all().order_by('-end')[0]
            self.college = last_enroll.college
            self.graduated = self.collegeenrollment_set.filter(graduated=True).count()
            self.program_years = last_enroll.program_years
            prev_enrollment = None
            for enrollment in self.collegeenrollment_set.filter(college_sequence__gt=0).order_by('college_sequence'):
                if prev_enrollment:
                    transfer, created = Withdrawl.objects.get_or_create(
                        college = prev_enrollment.college,
                        alumni = prev_enrollment.alumni,
                        date = prev_enrollment.end,
                    )
                    if created:
                        transfer.from_enrollment = True
                        transfer.save()
                prev_enrollment = enrollment
            self.semesters = str(self.collegeenrollment_set.filter(college=self.college).count())
            self.save()
