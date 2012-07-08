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

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from ecwsp.sis.models import Student, SchoolYear
from ecwsp.administration.models import Configuration

import datetime
import sys
import logging

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
    student =  models.ForeignKey(Student, related_name="student_attn", help_text="Start typing a student's first or last name to search")
    date = models.DateField(default=datetime.datetime.now)
    status = models.ForeignKey(AttendanceStatus)
    time = models.TimeField(blank=True,null=True)
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
    
    @property
    def edit(self):
        return "Edit"
        
    def save(self, *args, **kwargs):
        """Don't save Present """
        present, created = AttendanceStatus.objects.get_or_create(name="Present")
        if self.status != present:
            super(StudentAttendance, self).save(*args, **kwargs)
        else:
            try: self.delete()
            except: pass

def post_save_attendance_handler(sender, instance, **kwargs):
    """ Check for any triggers we should run """
    try:
        # Create work study attendance if student's workday is today
        if ('ecwsp.work_study' in settings.INSTALLED_APPS and
            Configuration.get_or_default("attendance_create_work_attendance", "False").value == "True" and
            instance.date == datetime.date.today() and
            instance.status.absent and
            hasattr(instance.student, 'studentworker') and
            instance.student.studentworker and
            datetime.date.today().isoweekday() == instance.student.studentworker.get_day_as_iso_date()
           ):
            from ecwsp.work_study.models import Attendance
            attn, created = Attendance.objects.get_or_create(
                student=instance.student.studentworker,
                absence_date = datetime.date.today(),
            )
            if created:
                attn.sis_attendance = instance
                attn.save()
    except:
        logging.error('Attendance trigger error', exc_info=True)
        
post_save.connect(post_save_attendance_handler, sender=StudentAttendance)


class AttendanceLog(models.Model):
    date = models.DateField(default=datetime.date.today)
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