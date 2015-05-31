from django.db import models
from ecwsp.sis.models import Faculty
from ecwsp.schedule.models import CourseSection, MarkingPeriod


class CourseSectionSync(models.Model):
    course_section = models.ForeignKey(CourseSection)
    marking_period = models.ForeignKey(MarkingPeriod)
    engrade_course_id = models.BigIntegerField(unique=True)

    class Meta:
        unique_together = (('course_section', 'marking_period'),)

    def __unicode__(self):
        return unicode(self.course_section)


class TeacherSync(models.Model):
    teacher = models.OneToOneField(Faculty)
    engrade_teacher_id = models.BigIntegerField(unique=True)

    def __unicode__(self):
        return unicode(self.teacher)
