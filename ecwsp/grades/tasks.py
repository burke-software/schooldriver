from celery.decorators import periodic_task
from .models import StudentMarkingPeriodGrade, StudentYearGrade
from ecwsp.sis.models import Student
from ecwsp.sis.helper_functions import all_tenants
from ecwsp.schedule.models import CourseEnrollment
from django_sis.celery import app
from django.conf import settings

@app.task
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


@app.task
@all_tenants
def build_grade_cache_task():
    build_grade_cache()
