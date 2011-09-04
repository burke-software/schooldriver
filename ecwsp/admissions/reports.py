from ecwsp.admissions.models import *
from ecwsp.sis.xlsReport import *
from ecwsp.sis.models import GradeLevel

import datetime

def report_process_statistics(year):
    titles = ['Year %s' % (year,) ,]
    data = []
    data.append(['Date', str(datetime.date.today())])
    
    # active prospects
    data.append([])
    data.append(['Admissions Status', '# of prospects'])
    applicants = Applicant.objects.filter(school_year=year)
    levels = AdmissionLevel.objects.all()
    for level in levels:
        lvl_applicants = applicants.filter(level=level).distinct()
        data.append([level, lvl_applicants.count()])
    
    # application decision
    data.append([])
    data.append(['# of Prospects by Application Decision'])
    for decision in ApplicationDecisionOption.objects.all():
        st_applicants = applicants.filter(application_decision=decision).distinct()
        data.append([decision, st_applicants.count()])
    
    # by year    
    data.append([])
    data.append(['# of Prospects by Grade'])
    for grade_level in GradeLevel.objects.all():
        yr_applicants = applicants.filter(year=grade_level).distinct()
        data.append([grade_level, yr_applicants.count()])
    
    report = xlsReport(data, titles, "Process Statistics.xls", heading="Process Statistics")
    return report.finish()