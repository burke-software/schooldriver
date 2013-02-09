from ecwsp.admissions.models import Applicant, AdmissionLevel, GradeLevel, ApplicationDecisionOption
from ecwsp.sis.xl_report import XlReport
from ecwsp.sis.models import GradeLevel

import datetime

def report_process_statistics(year):
    titles = ['Year %s' % (year,) ,]
    data = []
    data.append(['Date', str(datetime.date.today())])
    
    # active prospects
    data.append([])
    data.append(['Admissions Status', '# of prospects'])
    applicants = Applicant.objects.filter(school_year__in=year)
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
    
    report = XlReport(file_name="Process_Statistics")
    report.add_sheet(data, header_row=titles, title="Process Statistics", heading="Process Statistics")
    return report.as_download()