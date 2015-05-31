from django.db import models


class CourseSectionSync(models.Model):
    course_section = models.ForeignKey('schedule.CourseSection')
    marking_period = models.ForeignKey('schedule.MarkingPeriod')
    engrade_course_id = models.BigIntegerField(unique=True)

    class Meta:
        unique_together = (('course_section', 'marking_period'),)
    def __unicode__(self):
        return unicode(self.course_section)


class TeacherSync(models.Model):
    teacher = models.OneToOneField('sis.Faculty')
    engrade_teacher_id = models.BigIntegerField(unique=True)

    def __unicode__(self):
        return unicode(self.teacher)
