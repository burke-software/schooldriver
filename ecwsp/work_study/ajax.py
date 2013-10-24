from ecwsp.work_study.models import StudentWorker
from dajaxice.decorators import dajaxice_register

import json
import datetime

@dajaxice_register
def attendance_dashlet(request, date):
    if date:
        date = datetime.datetime.strptime(date, '%m/%d/%Y')
    else:
        date = datetime.date.today()
    weekday = date.isoweekday()
    if weekday == 1:
        weekday = 'M'
    elif weekday == 2:
        weekday = "T"
    elif weekday == 3:
        weekday = 'W'
    elif weekday == 4:
        weekday = 'TH'
    elif weekday == 5:
        weekday = 'F'
    print weekday
    working_today = StudentWorker.objects.filter(day=weekday, is_active=True, placement__isnull=False)
    without_timesheets = working_today.exclude(timesheet__date=date)
    
    return json.dumps({
        'working_today': working_today.count(),
        'without_timesheets': without_timesheets.count(),
    })
