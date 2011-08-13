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
from datetime import datetime

class Hours(models.Model):
    class Meta:
        verbose_name = "Hours"
        verbose_name_plural = "Hours"
        unique_together = ("student","date")
    student = models.ForeignKey('Volunteer')
    date = models.DateField(blank = False, null = False)
    hours = models.FloatField()
    approved = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(auto_now=True)
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
    name = models.CharField(max_length=200, blank=True)
    site = models.ManyToManyField('Site')
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    def __unicode__(self):
        return unicode(self.name)

class Volunteer(models.Model):
    student = models.OneToOneField('sis.Student') #string so that it looks up sis.Student after the fact.
    site = models.OneToOneField('Site', null=True, blank=True)
    site_approval = models.CharField(max_length=16, choices=(('Accepted','Accepted'),('Rejected', 'Rejected'),('Submitted', 'Submitted'),('Resubmitted', 'Resubmitted')), blank=True)
    site_supervisor = models.ForeignKey('SiteSupervisor', blank=True, null=True)
    attended_reflection = models.BooleanField(verbose_name = "Attended")
    contract = models.BooleanField()
    hours_record = models.BooleanField(verbose_name = "Hours Confirmed")
    hours_required = models.IntegerField(default=20, blank=True, null=True)
    comment = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(default = datetime.now)
    job_description = models.TextField(blank=True)
    def __unicode__(self):
        return unicode(self.student)
    def hours_completed(self):
        return self.hours_set.all().aggregate(Sum('hours'))['hours__sum']
