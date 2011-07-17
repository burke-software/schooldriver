from ecwsp.admissions.models import *
from ecwsp.sis.xlsReport import *
from ecwsp.sis.models import GradeLevel

import datetime

def report_process_statistics(year):
    titles = ['Process Statistics for year %s' % (year,) ,]
    data = []
    data.append(['Date', str(datetime.date.today())])
    
    # active prospects
    data.append(['Active Prospects'])
    data.append(['Admissions Status', '# of prospects'])
    applicants = Applicant.objects.filter(year=year)
    levels = AdmissionLevel.objects.all()
    for level in levels:
        lvl_applicants = applicants.filter(level=level).distinct()
        data.append([level, lvl_applicants.count()])
    
    # by year    
    data.append([])
    data.append(['# of prospects by grade'])
    for year in GradeLevel.objects.all():
        yr_applicants = applicants.filter(year=year).distinct()
        data.append([year, yr_applicants.count()])
    
    report = xlsReport(data, titles, "Process Statistics.xls", heading="Process Statistics")
    return report.finish()