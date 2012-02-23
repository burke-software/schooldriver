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

# obsoleted hack pending removal
"""
def credits_hack_thing(student):
    ''' get credits before benchmark grading, using an arbitrary date from the past '''
    credits = 0
    courses = student.course_set.filter(graded=True, marking_period__show_reports=True).exclude(omitcoursegpa__student=student).distinct()
    for c in courses:
        try:
            credits += float(c.get_credits_earned(date_report=date(2011, 6, 30)))
        except:
            pass
    return credits
"""

def benchmark_report_card(template, options, students, format="odt"):
    """ A TC-exclusive benchmark-based report card generator for a single marking period """
    """ lots of crap commented out is obsoleted by legit gpa calculator and will be removed soon """

    data = get_default_data()

    blank_grade = struct()
    blank_grade.comment = ""

    for_date = options['date']
    #try:
    school_year=SchoolYear.objects.filter(start_date__lt=for_date).order_by('-start_date')[0]
    attendance_marking_periods = MarkingPeriod.objects.filter(school_year=SchoolYear.objects.filter(start_date__lt=for_date)[0],
                                                  start_date__lt=for_date,
                                                  show_reports=True)
    marking_period = attendance_marking_periods.order_by('-start_date')[0]
    #except:
        # how do we really handle errors around here?
     #   return HttpResponse("Could not find a marking period for the date " + str(for_date) + ".")
        
    '''
    # for GPA calculation, how far into the year are we?
    year_mps = attendance_marking_periods.count()
    this_mp = None
    i = 1
    for mp in attendance_marking_periods.order_by('start_date'):
        if mp == marking_period:
            this_mp = i
            break
        i += 1
    year_fraction = float(this_mp) / float(year_mps) # just die ungracefully if this doesn't work
    '''

    for student in students:
        courses = Course.objects.filter(
            courseenrollment__user=student,
            graded=True,
        )
        courses = courses.filter(marking_period=marking_period).distinct().order_by('department')
        averages = {}
        denominators = {}
        student.courses = []
        student.hire4ed = None # otherwise appy has a conniption.
        for course in courses:
            Hire4Ed = False
            if course.department is not None:
                Hire4Ed = course.department.name == "Hire4Ed" # this seems expensive
            for aggregate in Aggregate.objects.filter(singleStudent=student, singleCourse=course, singleMarkingPeriod=marking_period):
                aggName = re.sub("[^A-Za-z]", "", aggregate.singleCategory.name)
                aggStruct = struct()
                aggStruct.name = aggregate.name # has become ugly; not used in template
                aggStruct.mark = aggregate.scale.spruce(aggregate.cachedValue)
                setattr(course, aggName, aggStruct)
                # Hire4Ed does not count toward student averages across academic classes
                if aggregate.cachedValue is not None:
                    # don't double-count standards
                    if Hire4Ed and aggregate.singleCategory.name != "Standards":
                        try:
                            course.average += aggregate.cachedValue
                            course.averageDenom += 1
                        except AttributeError:
                            course.average = aggregate.cachedValue
                            course.averageDenom = 1
                    try:
                        averages[aggName] += aggregate.cachedValue
                        denominators[aggName] += 1
                    except KeyError:
                        averages[aggName] = aggregate.cachedValue
                        denominators[aggName] = 1
            if not Hire4Ed:
                try:
                    courseAverageAgg = Aggregate.objects.get(singleCategory__name="Standards", singleStudent=student, singleCourse=course,
                                                             singleMarkingPeriod=marking_period)
                    course.average = courseAverageAgg.scale.spruce(courseAverageAgg.cachedValue)
                    #GAHH ALL SPRUCING AT THE END
                    course.usAverage = courseAverageAgg.cachedValue
                except:
                    pass
            items = []
        standards_category = Category.objects.get(name="Standards") # save time, move to top and do this once?
        for mark in Mark.objects.filter(item__category=standards_category, item__course=course,
                                        item__markingPeriod=marking_period,
                                        student=student, description="Session"):
        markItem = struct()
        markItem.name = mark.item.name
        markItem.range = mark.item.scale.range()
        markItem.mark = mark.mark
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
                markItem.mark = mark.item.scale.spruce(markItem.mark)
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

        # whoa, we actually calcuate real cumulative GPAs now!
        '''
        if student.cache_gpa is None:
            student.cache_gpa = student.calculate_gpa()
        try:
            student.cumulative_gpa = float(student.cache_gpa)
            student.credits = credits_hack_thing(student)
        except:
            student.cumulative_gpa = 0
            student.credits = 0
        '''
        if i > 0:
            student.session_gpa = Decimal(str(session_gpa / i)).quantize(Decimal(str(0.01)), ROUND_HALF_UP)
        '''
            student.cumulative_gpa *= student.credits
            student.cumulative_gpa += float(i) * year_fraction * float(student.session_gpa)
            student.credits += float(i) * year_fraction # this year doesn't count as a whole unless it's complete
            student.cumulative_gpa /= student.credits
            student.cumulative_gpa = Decimal(str(student.cumulative_gpa)).quantize(Decimal(str(0.01)), ROUND_HALF_UP)
        '''
        # don't fuck this up
        if student.session_gpa == student.calculate_gpa_mp(marking_period):
            print 'jnm Marking Period GPA Assertion PASSED!'
        else:
            print 'BADNESS! GPA calculation problem for', student, marking_period

        #Attendance for marking period
        i = 1
        student.absent_total = 0
        student.tardy_total = 0
        student.dismissed_total = 0
        student.attendance_marking_periods = []
        for mp in attendance_marking_periods.order_by('start_date'):
            absent = student.student_attn.filter(status__absent=True, date__range=(mp.start_date, mp.end_date)).count()
            tardy = student.student_attn.filter(status__tardy=True, date__range=(mp.start_date, mp.end_date)).count()
            dismissed = student.student_attn.filter(status__code="D", date__range=(mp.start_date, mp.end_date)).count()
            student.absent_total += absent
            student.tardy_total += tardy
            student.dismissed_total += dismissed
            amp = struct()
            amp.absent = absent
            amp.tardy = tardy
            amp.dismissed = dismissed
            amp.number = i
            student.attendance_marking_periods.append(amp)
            i += 1
    try:
        if options['student'].count == 1:
            data['student'] = options['student'][0]
    except: pass

    data['students'] = students
    data['school_year'] = school_year
    data['marking_period'] = marking_period.name # just passing object makes appy think it's undefined
    filename = 'output'
    return pod_save(filename, ".pdf", data, template)
    #return pod_save(filename, "." + str(format), data, template)
