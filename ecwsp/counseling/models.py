#   Copyright 2012 Burke Software and Consulting LLC
#   Author David M Burke <david@burkesoftware.com>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
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

from django.contrib.auth.models import User, Group
from django.db import models

import datetime

from ecwsp.sis.models import Student

class FollowUpAction(models.Model):
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return unicode(self.name)

class StudentMeeting(models.Model):
    students = models.ManyToManyField(Student)
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True)
    follow_up_action = models.ForeignKey(FollowUpAction,blank=True,null=True)
    follow_up_notes = models.CharField(max_length=2024,blank=True)
    reported_by = models.ForeignKey(User,limit_choices_to = {'groups__name': 'faculty'})
    def __unicode__(self):
        students = ''
        for student in self.students.all():
            students += '%s, ' % (student,)
        return '%s meeting with %s' % (unicode(self.reported_by),students[:-2])
    def display_students(self):
        txt = ''
        for student in self.students.all():
            txt += '%s, ' % (student)
        return txt[:-2]

class ReferralCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return unicode(self.name)

class ReferralReason(models.Model):
    category = models.ForeignKey(ReferralCategory)
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return '%s: %s' (unicode(self.category), unicode(self.name))

class ReferralForm(models.Model):
    classroom_teacher = models.ForeignKey(User,limit_choices_to = {'groups__name': 'faculty'},related_name='referral_classroom_teacher')
    date = models.DateField(default=datetime.date.today)
    referred_by = models.ForeignKey(User,limit_choices_to = {'groups__name': 'faculty'})
    student = models.ForeignKey(Student)
    comments = models.TextField(blank=True)
    referral_reasons = models.ManyToManyField(ReferralReason, blank=True,null=True)
