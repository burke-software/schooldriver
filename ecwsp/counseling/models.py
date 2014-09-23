from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.db import models
from ckeditor.fields import RichTextField
from ecwsp.sis.helper_functions import get_base_url
from ecwsp.sis.models import Student
from ecwsp.administration.models import Configuration
import datetime
import logging

class FollowUpAction(models.Model):
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return unicode(self.name)

class StudentMeetingCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return unicode(self.name)

class StudentMeeting(models.Model):
    students = models.ManyToManyField(Student, related_name="student_meeting_set")
    category = models.ForeignKey(StudentMeetingCategory,blank=True,null=True)
    date = models.DateField(default=datetime.date.today, validators=settings.DATE_VALIDATORS)
    notes = RichTextField(blank=True)
    follow_up_action = models.ForeignKey(FollowUpAction,blank=True,null=True)
    follow_up_notes = models.CharField(max_length=2024,blank=True)
    reported_by = models.ForeignKey(User,limit_choices_to = {'groups__name': 'faculty'})
    referral_form = models.ForeignKey('ReferralForm',blank=True,null=True,editable=False)
    file = models.FileField(upload_to='student_meetings',blank=True,null=True)
    def __unicode__(self):
        students = ''
        for student in self.students.all():
            students += u'{}, '.format(student)
        # DRY stands for DO repeat yourself, right?
        nice_user = u', '.join((self.reported_by.last_name, self.reported_by.first_name))
        if not len(nice_user): nice_user = self.reported_by.username
        return u'%s meeting with %s' % (nice_user,students[:-2])
    def display_students(self):
        txt = ''
        for student in self.students.all():
            txt += u'%s, ' % (student)
        return unicode(txt[:-2])
        
    class Meta:
        ordering = ('-date',)

class ReferralCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return unicode(self.name)

class ReferralReason(models.Model):
    category = models.ForeignKey(ReferralCategory)
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return '%s: %s' % (self.category, self.name)

class ReferralForm(models.Model):
    classroom_teacher = models.ForeignKey(User,limit_choices_to = {'groups__name': 'faculty'},related_name='referral_classroom_teacher')
    date = models.DateField(default=datetime.date.today, validators=settings.DATE_VALIDATORS)
    referred_by = models.ForeignKey(User,limit_choices_to = {'groups__name': 'faculty'})
    student = models.ForeignKey(Student, related_name="+")
    comments = models.TextField(blank=True)
    referral_reasons = models.ManyToManyField(ReferralReason, blank=True,null=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            new = True
        else:
            new = False
        super(ReferralForm, self).save(*args, **kwargs)
        if new:
            try:
                subject = 'New counseling referral for %s.' % (self.student,)
                msg = '%s has submitted a counseling referral form for %s. Click this link to view \n%s%s' % \
                (self.referred_by, self.student, get_base_url(), reverse('admin:counseling_referralform_change',args=(self.id,)),)
                from_addr = Configuration.get_or_default("From Email Address", "donotreply@cristoreyny.org").value
                to_addr = Configuration.get_or_default("counseling_referral_notice_email_to", "").value.split(',')
                if to_addr and to_addr != ['']:
                    send_mail(subject, msg, from_addr, to_addr)
            except:
                logging.error('Couldn\'t email counseling referral form.', exc_info=True)
    
    def __unicode__(self):
        return 'Referral %s - %s - %s' % (self.date, self.classroom_teacher, self.student)
