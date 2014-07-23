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
    teacher_selectable = models.BooleanField(default=False, )
    excused = models.BooleanField(default=False, )
    absent = models.BooleanField(default=False, help_text="Some statistics need to add various types of absent statuses, such as the number in parentheses in daily attendance.")
    tardy = models.BooleanField(default=False, help_text="Some statistics need to add various types of tardy statuses, such as the number in parentheses in daily attendance.")
    half = models.BooleanField(default=False, help_text="Half attendance when counting. DO NOT check off absent otherwise it will double count!")
    
    class Meta:
        verbose_name_plural = 'Attendance Statuses'
    
    def __unicode__(self):
        return unicode(self.name)


class CourseSectionAttendance(models.Model):
    """ Attendance taken at each course (section)
    It compares with the daily "student attendance" and is a way to verify
    students are not skipping classes.
    """
    student = models.ForeignKey(Student)
    course_section = models.ForeignKey('schedule.CourseSection')
    period = models.ForeignKey('schedule.Period', blank=True, null=True)
    date = models.DateField(default=datetime.datetime.now, validators=settings.DATE_VALIDATORS)
    time_in = models.TimeField(blank=True, null=True)
    status = models.ForeignKey(AttendanceStatus)
    notes = models.CharField(max_length=500, blank=True)
    def __unicode__(self):
        return unicode(self.student) + " " + unicode(self.date) + " " + unicode(self.status)
    
    def course_period(self):
        if self.course_section.coursemeet_set.filter(day=self.date.isoweekday()):
            return self.course_section.coursemeet_set.filter(day=self.date.isoweekday())[0].period


class StudentAttendance(models.Model):
    student = models.ForeignKey(Student, related_name="student_attn", help_text="Start typing a student's first or last name to search")
    date = models.DateField(default=datetime.datetime.now, validators=settings.DATE_VALIDATORS)
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
    if True:
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
    date = models.DateField(default=datetime.date.today, validators=settings.DATE_VALIDATORS)
    user = models.ForeignKey(User)
    course_section = models.ForeignKey('schedule.CourseSection')
    asp = models.BooleanField(default=False, help_text="ASP attendance, if unchecked this is for a homeroom")
    def __unicode__(self):
        return unicode(self.user) + " " + unicode(self.date)
