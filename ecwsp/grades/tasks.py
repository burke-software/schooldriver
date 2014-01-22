from celery.decorators import periodic_task
from celery.task.schedules import crontab
from .models import StudentMarkingPeriodGrade, StudentYearGrade
from ecwsp.sis.models import Student
from ecwsp.schedule.models import CourseEnrollment

@periodic_task(run_every=crontab(hour=1, minute=21))
def build_grade_cache():
    """ Rebuild all grade related cache in the world """
    StudentMarkingPeriodGrade.build_all_cache()
    StudentYearGrade.build_all_cache()
    for student in Student.objects.all():
        student.recalculate_gpa()
    for marking_period_grade in StudentMarkingPeriodGrade.objects.all():
        marking_period_grade.recalculate_grade()
    for year_grade in StudentYearGrade.objects.all():
        year_grade.recalculate_grade()
    for enrollment in CourseEnrollment.objects.all():
        enrollment.cache_grades()
