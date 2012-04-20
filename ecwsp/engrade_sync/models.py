#   Copyright 2011 David M Burke <david@davidmburke.com>
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

# These models link SWORD models to engrade data, usually this means storing
# SWORD's and Engrade's ids.

from django.db import models
from ecwsp.sis.models import *
from ecwsp.schedule.models import *

class CourseSync(models.Model):
    course = models.ForeignKey(Course)
    marking_period = models.ForeignKey(MarkingPeriod)
    engrade_course_id = models.BigIntegerField(unique=True)
    class Meta:
        unique_together = (('course', 'marking_period'),)
    def __unicode__(self):
        return unicode(self.course)

class TeacherSync(models.Model):
    teacher = models.ForeignKey(Faculty, unique=True)
    engrade_teacher_id = models.BigIntegerField(unique=True)
    def __unicode__(self):
        return unicode(self.teacher)
    