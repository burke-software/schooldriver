from django.db import models
from ecwsp.sis.models import *
from ecwsp.schedule.models import *

class CourseSync(models.Model):
    course = models.ForeignKey(CourseSection)
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
    
