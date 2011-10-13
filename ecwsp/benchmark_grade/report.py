from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from ecwsp.sis.models import *
from ecwsp.sis.uno_report import uno_save
from ecwsp.administration.models import *
from ecwsp.schedule.models import *
from ecwsp.schedule.calendar import *
from ecwsp.sis.report import *
from ecwsp.benchmark_grade.models import *

from ecwsp.appy.pod.renderer import Renderer
import tempfile
import os
import uno
from decimal import *

class struct(object):
    def __unicode__(self):
        return ""

def pod_benchmark_report_grade(template, options, students, format="odt", transcript=True, report_card=True):
    """ Generate report card and transcript grades via appy
    variables for apply:
    students                - contails all each student
    students.courses        - courses for the student (usually for report cards, one year)
    students.years          - years student is enrolled (and selected)
    students.years.courses  - courses for one year (usually for transcripts that span multiple years)
    year                    - Selected school year
    students.phone          - First phone number for student
    students.sat_highest    - Highest possible combination of SAT test scores. Looks for test named "SAT"
    students.years.ave      - Averaged grade for year
    students.years.total_days- School days this year
    students.years.absent   - Absents for year
    students.years.tardy    - Tardies for year
    students.years.dismissed - Dismissed for year
    studnets.years.credits  - Total credits for year
    """
        
    data = get_default_data()
    
    blank_grade = struct()
    blank_grade.comment = ""
    
    #if options['marking_period']:
    #    marking_periods = options['marking_period']
    #elif options['this_year']:
    #    marking_periods = MarkingPeriod.objects.filter(school_year=SchoolYear.objects.get(active_year=True))
    #else:
    for_date = options['date'] # In case we want a transcript from a future date
    marking_periods = MarkingPeriod.objects.filter(
        school_year=SchoolYear.objects.filter(
            start_date__lt=for_date
        ).order_by(
            '-start_date'
        )[0]
    ).filter(show_reports=True)
    
    for student in students:
        # for report_card
        if report_card:
            courses = Course.objects.filter(
                courseenrollment__user=student,
                graded=True,
            )
            courses = courses.filter(marking_period__in=marking_periods).distinct().order_by('department')
            averages = {}
            courseAverageAggs = "Standards", "Engagement", "Organization"
            for course in courses:
                course.average = 0
                denominator = 0
                for aggregate in Aggregate.objects.filter(singleStudent=student, singleCourse=course):
                    aggName = "".join(aggregate.name.split())
                    if aggregate.manualMark is not None:
                        try:
                            averages[aggName] += aggregate.manualMark
                        except KeyError:
                            averages[aggName] = aggregate.manualMark
                        if aggName in courseAverageAggs:
                            course.average += aggregate.manualMark
                            denominator += 1
                    setattr(course, aggName, aggregate.manualMark)
                if denominator > 0:
                    course.average = round(course.average / denominator, 2)
                else:
                    course.average = None
                items = []
                for item in Item.objects.filter(course=course):
                    markItem = struct()
                    markItem.name = item.name
                    try:
                        markItem.mark = item.mark_set.get(student=student).mark
                    except:
                        continue
                    items.append(markItem)
                course.items = items
            student.courses = courses
            if len(courses) > 0:
                for a in averages:
                    averages[a] /= len(courses)
                student.averages = averages
            #Attendance for marking period
            i = 1
            student.absent_total = 0
            student.tardy_total = 0
            student.dismissed_total = 0
            for mp in marking_periods.order_by('start_date'):
                absent = student.student_attn.filter(status__absent=True, date__range=(mp.start_date, mp.end_date)).count()
                tardy = student.student_attn.filter(status__tardy=True, date__range=(mp.start_date, mp.end_date)).count()
                dismissed = student.student_attn.filter(status__code="D", date__range=(mp.start_date, mp.end_date)).count()
                student.absent_total += absent
                student.tardy_total += tardy
                student.dismissed_total += dismissed
                setattr(student, "absent" + str(i), absent)
                setattr(student, "tardy" + str(i), tardy)
                setattr(student, "dismissed" + str(i), dismissed)
                i += 1
            while i <= 6:
                setattr(student, "absent" + str(i), "")
                setattr(student, "tardy" + str(i), "")
                setattr(student, "dismissed" + str(i), "")
                i += 1
    try:
        if options['student'].count == 1:
            data['student'] = options['student'][0]
    except: pass
    
    data['students'] = students
    filename = 'output'
    return pod_save(filename, "." + str(format), data, template)
