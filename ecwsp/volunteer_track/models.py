#   Copyright 2011 David M Burke
#   Author Callista Goss <calli@burkesoftware.com>
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


from django.db import models
from django.db.models import Sum
from django.contrib.localflavor.us.models import *
from django.contrib import messages

from datetime import datetime
import random

from ecwsp.administration.models import Configuration

class Hours(models.Model):
    student = models.ForeignKey('Volunteer')
    site = models.ForeignKey('Site')
    date = models.DateField(blank = False, null = False)
    hours = models.FloatField()
    time_stamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Hours"
        verbose_name_plural = "Hours"
        unique_together = ("student","date")
    def __unicode__(self):
        return unicode(self.hours)

class Site(models.Model):
    site_name = models.CharField(max_length=255, unique=True)
    site_address = models.CharField(max_length=511)
    site_city = models.CharField(max_length=768)
    site_state = models.CharField(max_length=30)
    site_zip = models.CharField(max_length=30)
    def __unicode__(self):
        return unicode(self.site_name)

class SiteSupervisor(models.Model):
    name = models.CharField(max_length=200)
    site = models.ForeignKey('Site',blank=True,null=True)
    phone = PhoneNumberField(max_length=40, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    def __unicode__(self):
        return unicode(self.name)

def get_hours_default():
    return Configuration.get_or_default('Volunteer Track Required Hours', default=20).value
class Volunteer(models.Model):
    student = models.OneToOneField('sis.Student') #string so that it looks up sis.Student after the fact.
    site = models.ForeignKey(Site,blank=True,null=True)
    site_approval = models.CharField(max_length=16, choices=(('Accepted','Accepted'),('Rejected', 'Rejected'),('Submitted', 'Submitted')), blank=True)
    site_supervisor = models.ForeignKey('SiteSupervisor', blank=True, null=True)
    attended_reflection = models.BooleanField(verbose_name = "Attended")
    contract = models.BooleanField()
    hours_record = models.BooleanField(verbose_name = "Hours Confirmed")
    hours_required = models.IntegerField(default=get_hours_default, blank=True, null=True)
    comment = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(default = datetime.now)
    job_description = models.TextField(blank=True)
    secret_key = models.CharField(max_length=20, blank=True, editable=False)
    email_queue = models.CharField(default="", max_length=1000, blank=True, editable=False, help_text="Used to store nightly notification emails")
    def __unicode__(self):
        return unicode(self.student)
        
    def save(self, *args, **kwargs):
        if self.id:
            old_volunteer = Volunteer.objects.get(id=self.id)
            if old_volunteer.site != self.site:
                self.email_queue += "Changed site from %s to %s. " % (unicode(old_volunteer.site), unicode(self.site))
            if old_volunteer.site_supervisor != self.site_supervisor:
                self.email_queue += "Changed supervisor from %s to %s. " % (unicode(old_volunteer.site_supervisor), unicode(self.site_supervisor))
            
            if old_volunteer.site_approval == "Submitted" and self.site_approval == "Accepted":
                try:
                    from django.core.mail import send_mail
                    from_email = Configuration.get_or_default("From Email Address",default="donotreply@change.me").value
                    msg = "Hello %s,\nYour site %s has been approved!"
                    emailEnd = Configuration.get_or_default("email", default="@change.me").value
                    send_to = str(self.student.username) + emailEnd
                    send_mail(subject, msg, from_email, [send_to])
                except:
                    if request.user.is_staff():
                        messages.error(request, 'Could not email student about site approval!')
                
        if not self.secret_key or self.secret_key == "":
            self.genKey()
            
        super(Volunteer, self).save(*args, **kwargs)
    def send_email_approval(self):
        """
        Send email to supervisor for approval
        """
        if not self.site_supervisor or not self.site_supervisor.email:
            return None
        try:
            sendTo = self.site_supervisor.email
            subject = "Volunteer hours approval for " + unicode(self.student)
            msg = "Hello " + unicode(self.site_supervisor.name) + ",\nPlease click on the link below to approve the time sheet\n" + \
                settings.BASE_URL + "/volunteer_tracker/approve?key=" + str(self.secret_key)
            from_addr = Configuration.get_or_default("From Email Address", "donotreply@example.org").value
            send_mail(subject, msg, from_addr, [sendTo])
        except:
            print >> sys.stderr, "Unable to send email to volunteer's supervisor! %s" % (self,)
    def genKey(self):
        key = ''
        alphabet = 'abcdefghijklmnopqrstuvwxyz1234567890_-'
        for x in random.sample(alphabet,random.randint(19,20)):
            key += x
        self.secret_key = key
    def hours_completed(self):
        return self.hours_set.all().aggregate(Sum('hours'))['hours__sum']
