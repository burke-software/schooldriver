from celery.decorators import periodic_task
from celery.task.schedules import crontab
from .models import StudentMarkingPeriodGrade#, StudentYearGrade

@periodic_task(run_every=crontab(hour=1, minute=21))
def build_grade_cache():
    StudentMarkingPeriodGrade.build_all_cache()
    #StudentYearGrade.build_all_cache()

def build_mp_grade_cache():
    #TODO: IMPLEMENT THIS!
    pass
