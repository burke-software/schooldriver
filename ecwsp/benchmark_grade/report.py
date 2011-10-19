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
import re
from decimal import *
from datetime import date

class struct(object):
    def __unicode__(self):
        return ""

def credits_hack_thing(student):
    credits = 0
    courses = student.course_set.filter(graded=True, marking_period__show_reports=True).exclude(omitcoursegpa__student=student).distinct()
    for c in courses:
        try:
            credits += float(c.get_credits_earned(date_report=date(2011, 6, 30)))
        except:
            pass
    return credits

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
    '''
    for_date = options['date'] # In case we want a transcript from a future date
    marking_periods = MarkingPeriod.objects.filter(
        school_year=SchoolYear.objects.filter(
            start_date__lt=for_date
        ).order_by(
            '-start_date'
        )[0]
    ).filter(show_reports=True)
    '''
    marking_periods = MarkingPeriod.objects.filter(name="Session 1")
    for student in students:
        # for report_card
        if report_card:
            courses = Course.objects.filter(
                courseenrollment__user=student,
                graded=True,
            )
            courses = courses.filter(marking_period__in=marking_periods).distinct().order_by('department')
            averages = {}
            denominators = {}
            student.courses = []
            student.hire4ed = None # otherwise appy has a conniption.
            for course in courses:
                Hire4Ed = False
                if course.department is not None:
                    Hire4Ed = course.department.name == "Hire4Ed" # this seems expensive
                for aggregate in Aggregate.objects.filter(singleStudent=student, singleCourse=course):
                    aggName = re.sub("[^A-Za-z]", "", aggregate.name)
                    # we'll pass the real name now, because I'm going to call "Precision & Accuracy" DailyPractice
                    aggStruct = struct()
                    aggStruct.name = aggregate.name
                    aggStruct.mark = aggregate.scale.spruce(aggregate.manualMark)
                    # Hire4Ed hack
                    if aggregate.name == "Precision & Accuracy":
                        aggName = "DailyPractice"
                    setattr(course, aggName, aggStruct)
                    # Hire4Ed does not count toward student averages across academic classes
                    if aggregate.manualMark is not None:
                        # don't double-count standards
                        if Hire4Ed and aggregate.name != "Standards":
                            try:
                                course.average += aggregate.manualMark
                                course.averageDenom += 1
                            except AttributeError:
                                course.average = aggregate.manualMark
                                course.averageDenom = 1
                        try:
                            averages[aggName] += aggregate.manualMark
                            denominators[aggName] += 1
                        except KeyError:
                            averages[aggName] = aggregate.manualMark
                            denominators[aggName] = 1
                if not Hire4Ed:
                    try:
                        courseAverageAgg = Aggregate.objects.get(name="Standards", singleStudent=student, singleCourse=course)
                        course.average = courseAverageAgg.scale.spruce(courseAverageAgg.manualMark)
                        #GAHH ALL SPRUCING AT THE END
                        course.usAverage = courseAverageAgg.manualMark
                    except:
                        pass
                items = []
                for item in Item.objects.filter(course=course):
                    markItem = struct()
                    markItem.name = item.name
                    markItem.range = item.scale.range()
                    try:
                        markItem.mark = item.mark_set.get(student=student).mark
                    except:
                        continue
                    if markItem.mark is not None:
                        items.append(markItem)
                        if Hire4Ed:
                            try:
                                course.average += markItem.mark
                                course.averageDenom += 1
                            except AttributeError:
                                course.average = markItem.mark
                                course.averageDenom = 1
                            try:
                                averages["Hire4Ed"] += markItem.mark
                                denominators["Hire4Ed"] += 1
                            except KeyError:
                                averages["Hire4Ed"] = markItem.mark
                                denominators["Hire4Ed"] = 1
                    markItem.mark = item.scale.spruce(markItem.mark)
                course.items = items
                try:
                    if Hire4Ed and course.averageDenom > 0:
                        course.average /= course.averageDenom
                except:
                    pass
                if Hire4Ed:
                    student.hire4ed = course
                else:
                    student.courses.append(course)
                print >> sys.stderr, unicode(student), str(type(student.hire4ed))
            for a in averages:
                if denominators[a] > 0:
                    averages[a] =  Decimal(str(averages[a] / denominators[a])).quantize(Decimal(str(0.01)), ROUND_HALF_UP)
            student.averages = averages
            # calculate gpas
            i = 0
            session_gpa = 0
            for course in student.courses: # at this point omits Hire4Ed
                try:
                    if course.usAverage is not None:
                        session_gpa += course.usAverage
                        i += 1
                except:
                    pass
            gpaAverages = "Engagement", "Organization", "Hire4Ed"
            for gA in gpaAverages:
                try:
                    if averages[gA] is not None:
                        session_gpa += averages[gA]
                        i += 1
                except:
                    pass
            if student.cache_gpa is None:
                student.cache_gpa = student.calculate_gpa()
            try:
                student.cumulative_gpa = float(student.cache_gpa)
                student.credits = credits_hack_thing(student)
            except:
                student.cumulative_gpa = 0
                student.credits = 0
            if i > 0:
                student.session_gpa = Decimal(str(session_gpa / i)).quantize(Decimal(str(0.01)), ROUND_HALF_UP)
                student.cumulative_gpa *= student.credits
                student.cumulative_gpa += float(i) / float(6) * float(student.session_gpa)
                student.credits += float(i) / float(6) # one-sixth for the first session
                student.cumulative_gpa /= student.credits
                student.cumulative_gpa = Decimal(str(student.cumulative_gpa)).quantize(Decimal(str(0.01)), ROUND_HALF_UP)

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
    #return pod_save(filename, ".pdf", data, template)
    return pod_save(filename, "." + str(format), data, template)
