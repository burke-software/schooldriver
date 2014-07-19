from django.db import models
from ecwsp.sis.models import *
from ecwsp.schedule.models import *

class CourseSectionSync(models.Model):
    course_section = models.ForeignKey(CourseSection)
    marking_period = models.ForeignKey(MarkingPeriod)
    engrade_course_id = models.BigIntegerField(unique=True)
    class Meta:
        unique_together = (('course_section', 'marking_period'),)
    def __unicode__(self):
        return unicode(self.course_section)

class TeacherSync(models.Model):
    teacher = models.ForeignKey(Faculty, unique=True)
    engrade_teacher_id = models.BigIntegerField(unique=True)
    def __unicode__(self):
        return unicode(self.teacher)
    
