#       models.py
#       
#       Copyright 2010 Cristo Rey New York High School
#        Author David M Burke <david@burkesoftware.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from django.db import models
from django.db.models.signals import m2m_changed
from django.db import connection
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from django.core import urlresolvers
from django.core.files import File
from django.conf import settings
from django.http import Http404
from django.dispatch import dispatcher
from django.db.models import signals
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.html import strip_tags
import re

import datetime
from datetime import timedelta
import hashlib
import sys
import urllib
from decimal import *
import random
from cStringIO import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from custom_field.models import *
from custom_field.custom_field import CustomFieldModel
from ckeditor.fields import RichTextField
import logging
from celery.contrib.methods import task

from ecwsp.administration.models import Configuration, Template
from ecwsp.sis.models import Student
from ecwsp.sis.helper_functions import CharNullField
from ecwsp.sis.template_report import TemplateReport

class CraContact(models.Model):
    name = models.ForeignKey(User)
    email = models.BooleanField(help_text="Recieve daily email listing all supervisor comments about student.")
    email_all = models.BooleanField(help_text="Recieve comments about all students")
    def __unicode__(self):
        return unicode(self.name.first_name) + " " + unicode(self.name.last_name)
    class Meta:
        verbose_name = "Contact CRA"

class PickupLocation(models.Model):
    import re
    from django.core.validators import RegexValidator
    namespace_regex = re.compile(r'^[A-z\-_1234567890]+$')
    location = models.CharField(max_length=20, unique=True, validators=[RegexValidator(regex=namespace_regex)], help_text="Must not contain spaces")
    long_name = models.CharField(max_length=255, blank=True)
    directions = models.TextField(blank=True)
    def __unicode__(self):
        return unicode(self.location)
    class Meta:
        verbose_name = "Companies: pickup"

class Contact(models.Model):
    #guid is for sugarcrm.  We just use 2 primary keys so both programs are happy.
    guid = models.CharField(unique=True, max_length=36, blank=True, null=True)
    fname = models.CharField(max_length=150, blank=True, null=True)
    lname = models.CharField(max_length=150, blank=True, null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    phone_cell = models.CharField(max_length=25, blank=True, null=True)
    fax = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField (max_length=75, blank=True, null=True)
    
    def __unicode__(self):
        return unicode(self.fname) + " " + unicode(self.lname) + " - " + unicode(self.email)
        
    class Meta:
        ordering = ('lname',)
        verbose_name = 'Contact Supervisor'
        
    def save(self, sync_sugar=True, *args, **kwargs):
        super(Contact, self).save(*args, **kwargs)
        if settings.SYNC_SUGAR and sync_sugar:
            from ecwsp.work_study.tasks import update_contact_to_sugarcrm
            update_contact_to_sugarcrm.delay(self)
    
    @property
    def edit_link(self):
        try:
            urlRes = urlresolvers.reverse('admin:work_study_contact_change', args=(self.id,))
            return '<a href="' + urlRes + '">' + str(self) + '</a>'
        except:
            return ""

class Company(models.Model, CustomFieldModel):
    name = models.CharField(max_length=255, unique=True)
    alternative_contract_template = models.FileField(
        upload_to='contracts_alt',
        blank=True,
        null=True,
        help_text="Optionally use this odt template instead of a global template for this particular company.")
    
    def __unicode__(self):
        return unicode(self.name)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.alternative_contract_template:
            filename = str(self.alternative_contract_template).lower()
            if not filename[-3:] in ('odt',):
                raise ValidationError('Invalid file type. Must be odt file.')
    
    def fte(self):
        try:
            noStudents = StudentWorker.objects.filter(placement__company=self,inactive=False).count()
            student_fte = Configuration.objects.get_or_create(name="Students per FTE")[0].value
            return noStudents/float(student_fte)
        except:
            return None
    
    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ('name',)


class WorkTeamUser(User):
    """
    Exists so that work study users can add and change user accounts but limited only to companies.
    """
    class Meta:
        proxy = True
    def save(self, *args, **kwargs):
        super(WorkTeamUser, self).save(*args, **kwargs)
        self.groups.add(Group.objects.get_or_create(name='Company')[0])

class WorkTeam(models.Model, CustomFieldModel):
    inactive = models.BooleanField(help_text="Will unset student's placements.")
    company = models.ForeignKey(Company, blank=True, null=True)
    team_name = models.CharField(max_length=255, unique=True)
    login = models.ManyToManyField(WorkTeamUser, blank=True, help_text="user from <a href=\"/admin/auth/user/\">here</a> that this company may login with, ensure user is in the \"company\" group so they have correct permissions")
    paying = models.CharField(max_length=1, choices=(('P', 'Paying'), ('N', 'Non-Paying'), ('F', 'Funded')), blank=True)
    funded_by = models.CharField(max_length=150, blank=True)
    cras = models.ManyToManyField(CraContact, blank=True, null=True)
    industry_type = models.CharField(max_length=100, blank=True)
    travel_route = models.CharField(max_length=50,help_text="Train or Van route",blank=True,db_column="train_line")
    stop_location = models.CharField(max_length=150, blank=True)
    am_transport_group = models.ForeignKey(PickupLocation,db_column="dropoff_location_id",blank=True, null=True, related_name="workteamset_dropoff", help_text="Group for morning dropoff. Can be used for work study attendance")
    pm_transport_group = models.ForeignKey(PickupLocation,blank=True,db_column="pickup_location_id",null=True, help_text="Group for evening pickup. Can be used for work study attendance. If same as dropoff, you can just not use this field.")
    address = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=150, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip = models.CharField(max_length=10, blank=True)
    directions_to = models.TextField(blank=True)
    directions_pickup = models.TextField(blank=True)
    map = models.ImageField(upload_to="maps", blank=True)
    use_google_maps = models.BooleanField()
    contacts = models.ManyToManyField(Contact, blank=True, help_text="All contacts at this company. You must select them here in order to select the primary contact for a student.")
    company_description = models.TextField(blank=True)
    job_description = models.TextField(blank=True)
    time_earliest = models.TimeField(blank=True, null=True)
    time_latest = models.TimeField(blank=True, null=True)
    time_ideal = models.TimeField(blank=True, null=True)
    
    class Meta:
        ordering = ('team_name',)
    
    def __unicode__(self):
        return unicode(self.team_name)
    
    # Legacy compatibility
    @property
    def dropoff_location(self):
        return self.am_transport_group
    @property
    def pickup_location(self):
        return self.pm_transport_group
    @property
    def train_line(self):
        return self.travel_route
    
    def save(self, *args, **kwargs):
        if self.use_google_maps:
            self.use_google_maps = False;
            image = urllib.urlretrieve("http://maps.google.com/maps/api/staticmap?sensor=false&size=500x400&markers=size:mid|color:red|" + \
                self.address + "," + self.city + "," + self.state + "," + self.zip)
            self.map.save(self.team_name + "_map.png", File(open(image[0])))
        if self.inactive:
            for student in self.studentworker_set.all():
                student.placement = None
                student.save()
        super(WorkTeam, self).save(*args, **kwargs)
        
    def delete(self):
        try:
            self.student_set.clear()
        except: pass
        super(WorkTeam, self).delete()
    
    def is_active(self):
        if StudentWorker.objects.filter(placement=self).count() > 0:
            return True
        else:
            return False
    
    def fte(self):
        try:
            noStudents = StudentWorker.objects.filter(placement=self).count()
            student_fte = Configuration.objects.get_or_create(name="Students per FTE")[0].value
            return noStudents/float(student_fte)
        except:
            return None
    
    def show_cras(self):
        txt = ""
        for cra in self.cras.all():
            txt += unicode(cra) + ", "
        return txt[:-2]
    
    @property
    def cra(self):
        """ For legacy purposes, self.cras was once a fk cra """
        return self.show_cras()
            
    @property
    def map_path(self):
        if self.placement and self.placement.map:
            map = self.placement.map.path
    
    def edit_link(self):
        try:
            urlRes = urlresolvers.reverse('admin:work_study_workteam_change', args=(self.id,))
            return '<a href="' + urlRes + '">' + str(self) + '</a>'
        except:
            return ""
    edit_link.allow_tags = True


class PaymentOption(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    cost_per_student = models.DecimalField(max_digits=10, decimal_places=2)
    def __unicode__(self):
        return unicode(self.name)
        
    def get_cost(self, students):
        return unicode(students * self.cost_per_student)
    
class StudentFunctionalResponsibility(models.Model):
    name = models.CharField(max_length=255)
    class Meta:
        verbose_name_plural = "Student Functional Responsibilities"
    def __unicode__(self):
        return unicode(self.name)
    
class StudentDesiredSkill(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return unicode(self.name)

class CompContract(models.Model, CustomFieldModel):
    company = models.ForeignKey(Company)
    company_name = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=datetime.datetime.now, validators=settings.DATE_VALIDATORS)
    school_year = models.ForeignKey('sis.SchoolYear', blank=True, null=True)
    number_students = models.IntegerField(blank=True, null=True)
    
    payment = models.ForeignKey(PaymentOption, default=9999, blank=True, null=True)
    student_functional_responsibilities = models.ManyToManyField(StudentFunctionalResponsibility, blank=True, null=True)
    student_functional_responsibilities_other = models.TextField(blank=True)
    student_desired_skills = models.ManyToManyField(StudentDesiredSkill, blank=True, null=True)
    student_desired_skills_other = models.TextField(blank=True)
    student_leave = models.BooleanField()
    student_leave_lunch = models.BooleanField(verbose_name="Student leaves for lunch")
    student_leave_errands = models.BooleanField(verbose_name="Student leaves for errands")
    student_leave_other = models.TextField(blank=True)
    
    signed = models.BooleanField()
    contract_file = models.FileField(upload_to='contracts', blank=True)
    ip_address = models.IPAddressField(blank=True, null=True, help_text="IP address when signed")
    
    def __unicode__(self):
        return unicode(self.company)
    class Meta:
        verbose_name = "Company Contract"
    
    @property
    def get_payment_cost(self, strip=True):
        """ Returns cost of payment plan * number of students
        strip: default True, removed .00 from the end """
        cost = self.payment.get_cost(self.number_students)
        if strip:
            return str(cost).split('.')[0]
        else:
            return str(cost)
        
    @property
    def student_leave_yesno(self):
        if self.student_leave:
            return "Yes"
        else:
            return "No"
    
    @property
    def student_leave_lunch_yesno(self):
        if self.student_leave_lunch:
            return "Student will leave for lunch"
        else:
            return "Student will not leave for lunch"
        
    @property
    def student_leave_errands_yesno(self):
        if self.student_leave_errands:
            return "Student will leave for errands"
        else:
            return "Student will not leave for errands"
        
    def generate_contract_file(self):
        report = TemplateReport()
        report.data['contract'] = self
        report.filename = unicode(self.company) + "_contract"
        if settings.PREFERED_FORMAT == "m":
            report.file_format = "doc"
        else:
            report.file_format = "odt"
        if self.company and self.company.alternative_contract_template:
            template = self.company.alternative_contract_template.file
        else:
            template = Template.get_or_make_blank(name="Work Study Contract").file.path
        if template :
            report_file = report.pod_save(template, get_tmp_file=True)
            self.contract_file.save(unicode(self.company) + "." + unicode(report.file_format), File(open(report_file)))
    
    #filename, ext, data, template
    def get_contract_as_pdf(self, ie=False, response=True):
        from ecwsp.sis.uno_report import uno_open, save_to_response, save_as
        """ Returns contract as a pdf file
        ie: Is the browser a piece of shit? Defaults to False
        response: When true returns an http response when false returns a django File()"""
        if self.contract_file:
            if response:
                document = uno_open(self.contract_file.path)
                response = save_to_response(document, self.contract_file.name.split('.')[0], "pdf")
                if ie:
                    response['Pragma'] = 'public'
                    response['Expires'] = '0'
                    response['Cache-Control'] = 'must-revalidate, post-check=0, pre-check=0'
                    response['Content-type'] = 'application-download'
                    response['Content-Disposition'] = 'attachment; filename="contract.pdf"'
                    response['Content-Transfer-Encoding'] = 'binary'
                return response
            else:
                document = uno_open(self.contract_file.path)
                return File(save_as(document,self.contract_file.name.split('.')[0], "pdf"))
        else:
            raise Http404

class Personality(models.Model):
    type = models.CharField(max_length=4, unique=True)
    description = models.TextField(blank=True)
    def __unicode__(self):
        return unicode(self.type)
    class Meta:
        ordering = ('type',)
        verbose_name_plural = 'Personality types'
    

class Handout33(models.Model):
    category = models.CharField(max_length=100)
    like = models.CharField(max_length=255)
    def __unicode__(self):
        return unicode(self.category) + ": " + unicode(self.like)
    class Meta:
        ordering = ('category', 'like',)

class StudentWorkerRoute(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    

class StudentWorker(Student):
    """A student in the database."""
    dayOfWeek = [
        ['M', 'Monday'],
        ['T', 'Tuesday'],
        ['W', 'Wednesday'],
        ['TH', 'Thursday'],
        ['F', 'Friday'],
    ]
    day = models.CharField(max_length=2, choices=dayOfWeek, blank=True, null=True, verbose_name="Working Day")
    transport_exception = models.CharField(
        max_length=2,
        blank=True,
        choices = (('AM','No AM'),('PM','No PM'),('NO','None'))
    )
    #fax = models.BooleanField(help_text="Check if student may fax time sheet instead of going to check-in, shows up on attendance", verbose_name="Text Time Sheet")
    work_permit_no = CharNullField(max_length=10, blank=True, null=True, unique=True)
    placement = models.ForeignKey(WorkTeam, blank=True, null=True, )
    school_pay_rate = models.DecimalField(blank=True, max_digits=5, decimal_places=2, null=True)
    student_pay_rate = models.DecimalField(blank=True, max_digits=5, decimal_places=2, null=True)
    primary_contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, blank=True, null=True, help_text="This is the primary supervisor. Emails will be sent to this person. If the contact you want is not showing you may need to add them to the company. New contacts will never automatically be assigned to a company unless the supervisor adds them.")
    personality_type = models.ForeignKey(Personality, blank=True, null=True)
    handout33 = models.ManyToManyField(Handout33, blank=True, null=True)
    adp_number = models.CharField(max_length=5, blank=True, verbose_name="ADP Number")
    
    am_route = models.ForeignKey(StudentWorkerRoute, blank=True, null=True, related_name="am_student_set")
    pm_route = models.ForeignKey(StudentWorkerRoute, blank=True, null=True, related_name="pm_student_set")
    
    class Meta:
        ordering = ('inactive','lname','fname',)
    
    def company(self):
        try:
            comp = self.placement
            urlRes = urlresolvers.reverse('admin:work_study_workteam_change', args=(comp.id,))
            return '<a href="' + urlRes + '">' + str(comp) + '</a>'
        except:
            return ""
    company.allow_tags = True
    
    @property
    def fax(self):
        """ Legacy "fax" support
        """
        if self.transport_exception == "PM":
            return True
        return False
    
    def get_day_as_iso_date(self):
        if self.day == 'M':
            return 1
        elif self.day == 'T':
            return 2
        elif self.day == 'W':
            return 3
        elif self.day == 'TH':
            return 4
        elif self.day == 'F':
            return 5
    
    @property
    def get_contact(self):
        if self.primary_contact:
            return self.primary_contact
        if self.placement:
            contacts = self.placement.contacts.all()
            if contacts:
                return contacts[0]
        return None
    
    def contact(self):
        contact = self.get_contact
        try:
            urlRes = urlresolvers.reverse('admin:work_study_contact_change', args = (contact.id,))
            return '<a href="' +urlRes + '">' + str(contact)
        except:
            return ""
    contact.allow_tags = True
    
    def edit_link(self):
        try:
            urlRes = urlresolvers.reverse('admin:work_study_studentworker_change', args=(self.id,))
            return '<a href="' + urlRes + '">' + unicode(self) + '</a>'
        except:
            return ""
    edit_link.allow_tags = True
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.id:
            if Student.objects.filter(username=self.username):
                raise ValidationError('Username must be unique.')
    
    # Override save, if placement changes record change in history table
    def save(self, *args, **kwargs):
        try:
            previous = StudentWorker.objects.get(id=self.id)
            if previous.placement != self.placement:
                history = CompanyHistory(student = self, placement = previous.placement)
                history.save()
                # set primary contact to None if company has changed and p_contact isn't explicitly set
                if previous.primary_contact == self.primary_contact:
                    self.primary_contact = None
        except:
            pass
        
        if self.primary_contact and self.placement:
            self.placement.contacts.add(self.primary_contact)
        
         # set pay rates
        if not self.school_pay_rate and not self.student_pay_rate:
            try:
                self.school_pay_rate = Decimal(Configuration.get_or_default("school pay rate per hour", default="13.00").value)
                self.student_pay_rate = Decimal(Configuration.objects.get("student pay rate per hour", default="9").value)
            except:
                pass
        super(StudentWorker, self).save(*args, **kwargs)
    
    def pickUp(self):
        try: return self.placement.pickup_location
        except: return ""
    
    def cra(self):
        try: return self.placement.cra
        except: return ""
    
    def __unicode__(self):
        return unicode(self.lname) + ", " + unicode(self.fname)


class Survey(models.Model):
    survey = models.CharField(max_length=255, help_text="Title of Survey ex: MP2 2010")
    student = models.ForeignKey(StudentWorker, limit_choices_to={'inactive': False})
    company = models.ForeignKey(WorkTeam, blank=True, null=True)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=510, blank=True)
    date = models.DateField(default=datetime.datetime.now, validators=settings.DATE_VALIDATORS)
    def save(self, *args, **kwargs):
        if self.company == None:
            self.company = self.student.placement
        super(Survey, self).save(*args, **kwargs)
    class Meta:
        ordering = ('survey','student','question')
    
    
# student's company history, logs each job the student worked at    
class CompanyHistory(models.Model):
    student = models.ForeignKey(StudentWorker)
    placement = models.ForeignKey(WorkTeam)
    date = models.DateField(default=datetime.datetime.now, validators=settings.DATE_VALIDATORS)
    fired = models.BooleanField()
    
    def getStudent(self):
        if self.student != None:
            return self.student
        else:
            return "Error no student"
    
    def __unicode__(self):
        try:
            return unicode(self.getStudent()) + " left " + unicode(self.placement) + " on " + unicode(self.date)
        except:
            return "Company History Object"
    
    class Meta:
        verbose_name_plural = "Companies: history"
        ordering = ('-date',)
        unique_together = ('student', 'placement', 'date')


class PresetComment(models.Model):
    comment = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.comment
        
    class Meta:
        ordering = ('comment',)


class StudentInteraction(models.Model):
    student = models.ManyToManyField(StudentWorker, limit_choices_to={'inactive': False}, blank=True, help_text="A email will automatically be sent to the CRA of this student if type is mentoring")
    reported_by = models.ForeignKey(User, blank=True, null=True)
    date = models.DateField(auto_now_add=True, validators=settings.DATE_VALIDATORS)
    type = models.CharField(max_length=1, choices=(('M', 'Mentoring'), ('D', 'Discipline'), ('P', 'Parent'), ('C', 'Company'), ('S', 'Supervisor'), ('O', 'Other')))
    comments = models.TextField(blank=True)
    preset_comment = models.ManyToManyField(PresetComment, blank=True, help_text="Double click on the comment on the left you to add. Or click the plus to add a new preset comment")
    companies = models.ManyToManyField(WorkTeam,  blank=True)
    
    def save(self, *args, **kwargs):
        if not self.id: new = True
        else: new = False
        super(StudentInteraction, self).save(*args, **kwargs)
        #email if needed
        if self.student.count() >= 1 and new:
            try:
                stu = self.student.all()[0]
                subject = unicode(self)
                msg = "Hello CRA " + unicode(stu.placement.cra.name.first_name) + ",\n"
                for aStudent in self.student.all():
                    msg += unicode(aStudent.fname) + " " + unicode(aStudent.lname) + ", "
                msg = msg[:-2] + " had a mentor meeting on " + unicode(self.date) + "\n" + unicode(self.comments) + "\n"
                for com in self.preset_comment.all():
                    msg += unicode(com) + "\n"
                from_addr = Configuration.get_or_default("From Email Address", "donotreply@cristoreyny.org").value
                send_mail(subject, msg, from_addr, [unicode(stu.placement.cra.name.email)])
            except:
                print >> sys.stderr, "warning: could not email CRA"
    
    def students(self):
        if self.student.count() == 1:
            return self.student.all()[0]
        elif self.student.count() > 1:
            return "Multiple students"
        else:
            return None
    
    def comment_Brief(self):
        txt = self.comments[:100] 
        for preCom in self.preset_comment.all():
            txt += ".." + str(preCom)[:40]
        return txt[:160]
    
    def cra(self):
        try:
            if self.student.count() == 1:
                stu = self.student.all()[0]
                comp = WorkTeam.objects.get(id=stu.placement.id)
                cra = CraContact.objects.get(id=comp.cra.id)
                return cra
            else:
                return ""
        except:
            return ""
    
    def __unicode__(self):
        # don't attempt to traverse a m2m if we're not actually in the database yet
        if self.pk and self.student.count() == 1:
            stu = self.student.all()[0]
            return unicode(stu) + " " + unicode(self.date)
        return "Interaction: " + unicode(self.date)
        
# this handler sets the company field in student interaction based on student
# company when it was added
def set_stu_int_placement(sender, instance, action, reverse, model, pk_set, *args, **kwargs):
    if action == "post_add":
        for id in pk_set:
            student = StudentWorker.objects.get(id=id)
            if student.placement:
                instance.companies.add(student.placement)
        instance.save()
m2m_changed.connect(set_stu_int_placement, sender=StudentInteraction.student.through)

def get_next_rank():
    """ Return next ranking """
    try:
        return TimeSheetPerformanceChoice.objects.order_by('-rank')[0].id + 1
    except IndexError:
        return 1
class TimeSheetPerformanceChoice(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rank = models.IntegerField(unique=True, default=get_next_rank, help_text="Must be unique. Convention is that higher numbers are better.")
    
    class Meta:
        ordering = ('rank',)
    
    def edit(self):
        return "Edit"
    
    def __unicode__(self):
        return self.name
    
    
class TimeSheet(models.Model):
    student = models.ForeignKey(StudentWorker)
    for_pay = models.BooleanField(help_text="Student is working over break and will be paid separately for this work.")
    make_up = models.BooleanField(help_text="Student is making up a missed day.", verbose_name="makeup")
    company = models.ForeignKey(WorkTeam) # Because a student's company can change but this shouldn't.
    creation_date = models.DateTimeField(auto_now_add=True, validators=settings.DATE_VALIDATORS)
    date = models.DateField(validators=settings.DATE_VALIDATORS)
    time_in = models.TimeField()
    time_lunch = models.TimeField()
    time_lunch_return = models.TimeField()
    time_out = models.TimeField()
    hours = models.DecimalField(blank=True, max_digits=4, decimal_places=2, null=True)
    school_pay_rate = models.DecimalField(blank=True, max_digits=5, decimal_places=2, null=True, help_text="Per hour pay rate the school is recieving from a company")
    student_pay_rate = models.DecimalField(blank=True, max_digits=5, decimal_places=2, null=True, help_text="Per hour pay rate the student is actually recieving")
    school_net = models.DecimalField(blank=True, max_digits=6, decimal_places=2, null=True)
    student_net = models.DecimalField(blank=True, max_digits=6, decimal_places=2, null=True)
    approved = models.BooleanField(verbose_name="approve")
    student_accomplishment = models.TextField(blank=True)
    performance = models.ForeignKey(TimeSheetPerformanceChoice, blank=True,null=True)
    supervisor_comment = models.TextField(blank=True)
    show_student_comments = models.BooleanField(default=True)
    supervisor_key = models.CharField(max_length=20, blank=True)
    cra_email_sent = models.BooleanField(help_text="This time sheet was sent to a cra via nightly email", editable=False)
    
    def student_Accomplishment_Brief(self):
        return unicode(self.student_accomplishment[:30])
    student_Accomplishment_Brief.short_description = "stu accomp."
        
    def supervisor_Comment_Brief(self):
        return unicode(self.supervisor_comment[:40])
    supervisor_Comment_Brief.short_description = "super comment"
    
    def genKey(self):
        key = ''
        alphabet = 'abcdefghijklmnopqrstuvwxyz1234567890_-'
        for x in random.sample(alphabet,20):
            key += x
        self.supervisor_key = key.strip('-')
        
    def __unicode__(self):
        return unicode(self.student) + " " + unicode(self.date)
    
    @task()
    def emailStudent(self, show_comment=True):
        try:
            sendTo = self.student.get_email
            subject = "Time Sheet approved for " + unicode(self.student)
            if show_comment:
                msg = "Hello " + unicode(self.student) + ",\nYour time card for " + self.date.strftime("%x") + " was approved. Your rating was " + unicode(self.performance) + " \nYour supervisor's comment was \"" \
                    + unicode(self.supervisor_comment) + "\""
            else:
                msg = "Hello " + unicode(self.student) + ",\nYour time card for " + self.date.strftime("%x") + " was approved."
            from_addr = Configuration.get_or_default("From Email Address", "donotreply@cristoreyny.org").value
            send_mail(subject, msg, from_addr, [str(sendTo)])
        except:
            logging.warning('Could not email student', exc_info=True, extra={
                'exception': sys.exc_info()[0],
                'exception2': sys.exc_info()[1],
            })
        
    def save(self, *args, **kwargs):
        email = False
        emailStu = False
        
        if not self.supervisor_key or self.supervisor_key == "":
            # Use previous key if one exists
            if self.id:
                ts = TimeSheet.objects.get(id=self.id)
                self.supervisor_key = ts.supervisor_key
            else:
                self.genKey()
                email = True
        
        # set hours
        hours = self.time_lunch.hour - self.time_in.hour
        mins = self.time_lunch.minute - self.time_in.minute
        hours += self.time_out.hour - self.time_lunch_return.hour
        mins += self.time_out.minute - self.time_lunch_return.minute
        hours += mins/Decimal(60)
        self.hours = hours
        
        # set pay rates
        if self.for_pay and not self.school_pay_rate and not self.student_pay_rate:
            try:
                self.school_pay_rate = self.student.school_pay_rate
                self.student_pay_rate = self.student.student_pay_rate
            except:
                print >> sys.stderr, "warning: pay rate for company not set. "
        
        # set payment net sum
        if self.school_pay_rate:
            self.school_net = self.hours * self.school_pay_rate
        if self.student_pay_rate:
            self.student_net = self.hours * self.student_pay_rate
        
        super(TimeSheet, self).save(*args, **kwargs)
        
        self.student = StudentWorker.objects.get(id=self.student.id) # refresh data for p contact
        if email and self.student.primary_contact:
            try:
                sendTo = self.student.primary_contact.email
                subject = "Time Sheet for " + str(self.student)
                msg = "Hello " + unicode(self.student.primary_contact.fname) + ",\nPlease click on the link below to approve the time sheet\n" + \
                    settings.BASE_URL + "/work_study/approve?key=" + str(self.supervisor_key)
                from_addr = Configuration.get_or_default("From Email Address", "donotreply@cristoreyny.org").value
                send_mail(subject, msg, from_addr, [sendTo])
            except:
                print >> sys.stderr, "Unable to send email to supervisor! %s" % (self,)

class AttendanceFee(models.Model):
    name = models.CharField(max_length=255)
    value = models.IntegerField(help_text="Dollar value of attendance fee")
    def __unicode__(self):
        return str(self.name) + " $" + str(self.value) 
    class Meta:
        verbose_name_plural = "Attendances: fees"
        
class AttendanceReason(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Attendances: Reason"
        
class Attendance(models.Model):
    student = models.ForeignKey(StudentWorker, help_text="Student who is absent this day")
    absence_date = models.DateField(default=datetime.datetime.now, verbose_name="date", validators=settings.DATE_VALIDATORS)
    tardy = models.CharField(verbose_name="Status", max_length=1, choices=(("P", "Present"),("A", "Absent/Half Day"),("T", "Tardy"),("N", "No Timesheet")),default="P")
    tardy_time_in = models.TimeField(blank=True,null=True)
    makeup_date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    fee = models.ForeignKey(AttendanceFee, blank=True, null=True)
    paid = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, help_text="Dollar value student has paid school for a fee.")
    billed = models.BooleanField(help_text="Has the student been billed for this day?")
    reason = models.ForeignKey(AttendanceReason, blank=True, null=True)
    half_day = models.BooleanField(help_text="Missed only half day")
    waive = models.BooleanField(help_text="Does not need to make up day at work.")
    notes = models.CharField(max_length=255, blank=True)
    if 'ecwsp.attendance' in settings.INSTALLED_APPS:
        sis_attendance = models.ForeignKey('attendance.StudentAttendance',blank=True,null=True,editable=False,on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return unicode(self.student) + " absent on " + unicode(self.absence_date)
        
    class Meta:
        unique_together = ('student', 'absence_date')
        verbose_name_plural = 'Attendance'


class ClientVisit(models.Model):
    dol = models.BooleanField()
    date = models.DateField(default=datetime.datetime.now, validators=settings.DATE_VALIDATORS)
    student_worker = models.ForeignKey('StudentWorker', blank=True, null=True)
    cra = models.ForeignKey(CraContact, blank=True, null=True)
    company = models.ForeignKey(WorkTeam)
    follow_up_of = models.ForeignKey('ClientVisit', blank=True, null=True, help_text="This report is a follow of up selected report")
    supervisor = models.ManyToManyField(Contact, blank=True, null=True)
    choices = (
        ('4', "Above and Beyond"),
        ('3', "Represents Level of Proficiency"),
        ('2', "On the way with some help"),
        ('1', "Need Immediate Intervention"),
    )
    attendance_and_punctuality = models.CharField(max_length=1, choices=choices, blank=True)
    attitude_and_motivation = models.CharField(max_length=1, choices=choices, blank=True)
    productivity_and_time_management = models.CharField(max_length=1, choices=choices, blank=True)
    ability_to_learn_new_tasks = models.CharField(max_length=1, choices=choices, blank=True)
    professional_appearance = models.CharField(max_length=1, choices=choices, blank=True)
    interaction_with_coworkers = models.CharField(max_length=1, choices=choices, blank=True)
    initiative_and_self_direction = models.CharField(max_length=1, choices=choices, blank=True)
    accuracy_and_attention_to_detail = models.CharField(max_length=1, choices=choices, blank=True)
    organizational_skills = models.CharField(max_length=1, choices=choices, blank=True)
    observations = models.TextField(blank=True)
    supervisor_comments = models.TextField(blank=True)
    student_comments = models.TextField(blank=True)
    job_description = models.TextField(blank=True)
    env_choices = (
        ('C', 'Safe / Compliant'),
        ('N', 'Not Compliant'),
    )
    work_environment = models.CharField(max_length=1, blank=True, choices=env_choices)
    notify_mentors = models.BooleanField(help_text = "Email this report out too all mentors (those in the mentors group)")
    notes = models.TextField(blank=True)
    
    def __unicode__(self):
        return unicode(self.company) + ": " + unicode(self.date)
        
    def comment_brief(self):
        return unicode(self.notes[:150]) + "..."
        
    def student(self):
        students = StudentWorker.objects.filter(placement=self.company)
        output = ""
        for student in students:
            output += student.fname + " " + student.lname + ", "
        return output
    
    def save(self, *args, **kwargs):
        super(ClientVisit, self).save(*args, **kwargs)
        if self.notify_mentors:
            try:
                users = User.objects.filter(groups__name='mentor')
                sendTo = []
                for user in users:
                    sendTo.append(user.email)
                subject = "CRA visit at " + unicode(self.company)
                msg = "A CRA report has been entered for " + unicode(self.company) + " on " + unicode(self.date) + ".\n" + unicode(self.notes)
                from_addr = Configuration.get_or_default("From Email Address", "donotreply@cristoreyny.org").value
                send_mail(subject, msg, from_addr, sendTo)
            except:
                print >> sys.stderr, "warning: could not email mentors"


class MessageToSupervisor(models.Model):
    """ Stores a message to be shown to students for a specific amount of time
    """
    message = RichTextField(help_text="This message will be shown to supervisors when they log in.")
    start_date = models.DateField(default=datetime.date.today, validators=settings.DATE_VALIDATORS)
    end_date = models.DateField(default=datetime.date.today, validators=settings.DATE_VALIDATORS)
    def __unicode__(self):
        # django.utils.html has a strip_entities(), but it's undocumented
        # so snatch up it's regular expression and use it here!
        return re.sub(r'&(?:\w+|#\d+);', '', strip_tags(self.message))
