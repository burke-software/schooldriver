from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from ecwsp.sis.models import *
from ecwsp.sis.uno_report import uno_save
from ecwsp.administration.models import *
from ecwsp.schedule.models import *
from ecwsp.schedule.calendar import *
from ecwsp.sis.report import *
from ecwsp.benchmark_grade.models import *
from ecwsp.benchmark_grade.utility import benchmark_find_calculation_rule, gradebook_get_average

import tempfile
import os
import uno
import re
from decimal import *
from datetime import date

class struct(object):
    def __unicode__(self):
        return ""

def benchmark_report_card(template, options, students, format="odt"):
    PASSING_GRADE = 3 # TODO: pull config value. Roche has it set to something crazy now and I don't want to deal with it

    data = get_default_data()
    for_date = options['date']
    school_year = SchoolYear.objects.filter(start_date__lt=for_date).order_by('-start_date')[0]
    calculation_rule = benchmark_find_calculation_rule(school_year)
    attendance_marking_periods = MarkingPeriod.objects.filter(school_year=school_year,
                                                  start_date__lt=for_date,
                                                  show_reports=True)
    marking_period = attendance_marking_periods.order_by('-start_date')[0]
    for student in students:
        student.courses = Course.objects.filter(
            courseenrollment__user=student,
            graded=True,
            marking_period=marking_period,
        ).distinct().order_by('department')
        student.count_total_by_category_name = {}
        student.count_missing_by_category_name = {}
        student.count_passing_by_category_name = {}
        for course in student.courses:
            course.average = gradebook_get_average(student, course, None, marking_period, None)
            course.current_marking_periods = course.marking_period.filter(start_date__lt=for_date).order_by('start_date')
            course.categories = Category.objects.filter(item__course=course, item__mark__student=student).distinct()
            course.category_by_name = {}
            for category in course.categories:
                category.weight_percentage = calculation_rule.per_course_category_set.get(category=category, apply_to_departments=course.department).weight * 100
                category.weight_percentage = category.weight_percentage.quantize(Decimal('0'), ROUND_HALF_UP)
                category.overall_count_total = 0
                category.overall_count_missing = 0
                category.overall_count_passing = 0
                for course_marking_period in course.current_marking_periods:
                    course_marking_period.category = category
                    course_marking_period.category.average = gradebook_get_average(student, course, category, marking_period, None)
                    items = Item.objects.filter(course=course, marking_period=marking_period, category=category, mark__student=student).annotate(best_mark=Max('mark__mark')).exclude(best_mark=None)
                    course_marking_period.category.count_total = items.exclude(best_mark=None).distinct().count()
                    course_marking_period.category.count_missing = items.filter(best_mark__lt=PASSING_GRADE).distinct().count()
                    course_marking_period.category.count_passing = items.filter(best_mark__gte=PASSING_GRADE).distinct().count()
                    if course_marking_period.category.count_total:
                        course_marking_period.category.count_percentage = (Decimal(course_marking_period.category.count_passing) / course_marking_period.category.count_total * 100).quantize(Decimal('0', ROUND_HALF_UP))

                    if course.department is not None and course.department.name == 'Corporate Work Study': # TODO: Remove this terrible hack
                        course_marking_period.category.count_passing = course_marking_period.category.count_total
                        course_marking_period.category.count_missing = 0
                        course_marking_period.category.count_percentage = 100

                    category.overall_count_total += course_marking_period.category.count_total
                    category.overall_count_missing += course_marking_period.category.count_missing
                    category.overall_count_passing += course_marking_period.category.count_passing

                    item_names = items.values_list('name').distinct()
                    course_marking_period.category.item_groups = []
                    for item_name_tuple in item_names:
                        item_name = item_name_tuple[0]
                        item_group = struct()
                        item_group.name = item_name
                        item_group.items = items.filter(name=item_name).distinct()
                        course_marking_period.category.item_groups.append(item_group)

                    course_marking_period.category_by_name = getattr(course_marking_period, 'category_by_name', {})
                    course_marking_period.category_by_name[category.name] = course_marking_period.category
                    # the last time through the loop is the most current marking period,
                    # so give that to anyone who doesn't request an explicit marking period
                    #category = course_marking_period.category

                course.category_by_name[category.name] = category
                if category.overall_count_total:
                    category.overall_count_percentage = (Decimal(category.overall_count_passing) / category.overall_count_total * 100).quantize(Decimal('0', ROUND_HALF_UP))
                student.count_total_by_category_name[category.name] = student.count_total_by_category_name.get(category.name, 0) + category.overall_count_total
                student.count_missing_by_category_name[category.name] = student.count_missing_by_category_name.get(category.name, 0) + category.overall_count_missing
                student.count_passing_by_category_name[category.name] = student.count_passing_by_category_name.get(category.name, 0) + category.overall_count_passing

        student.count_percentage_by_category_name = {}
        for category_name, value in student.count_total_by_category_name.items():
            if value:
                student.count_percentage_by_category_name[category_name] = (Decimal(student.count_passing_by_category_name[category_name]) / value * 100).quantize(Decimal('0', ROUND_HALF_UP))

        # make categories available 
            
        student.session_gpa = student.calculate_gpa_mp(marking_period)
        # Cannot just rely on student.gpa for the cumulative GPA; it does not reflect report's date
        student.current_report_cumulative_gpa = student.calculate_gpa(for_date)


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

    data['students'] = students
    data['school_year'] = school_year
    data['marking_period'] = marking_period.name # just passing object makes appy think it's undefined
    filename = 'output'
    return pod_save(filename, ".pdf", data, template)
    #return pod_save(filename, "." + str(format), data, template)

def bleh_benchmark_report_card(template, options, students, format="odt"):
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
            for aggregate in Aggregate.objects.filter(student=student, course=course, marking_period=marking_period).exclude(category=None):
                aggName = re.sub("[^A-Za-z]", "", aggregate.category.name)
                aggStruct = struct()
                aggStruct.name = aggregate.name # has become ugly; not used in template
                aggStruct.mark = aggregate.cached_value
                setattr(course, aggName, aggStruct)
                # Hire4Ed does not count toward student averages across academic classes
                if aggregate.cached_value is not None:
                    # don't double-count standards
                    if Hire4Ed and aggregate.category.name != "Standards":
                        try:
                            course.average += aggregate.cached_value
                            course.averageDenom += 1
                        except AttributeError:
                            course.average = aggregate.cached_value
                            course.averageDenom = 1
                    try:
                        averages[aggName] += aggregate.cached_value
                        denominators[aggName] += 1
                    except KeyError:
                        averages[aggName] = aggregate.cached_value
                        denominators[aggName] = 1
            if not Hire4Ed:
                try:
                    courseAverageAgg = Aggregate.objects.get(category__name="Standards", student=student, course=course,
                                                             marking_period=marking_period)
                    course.average = courseAverageAgg.cached_value
                    #GAHH ALL SPRUCING AT THE END
                    course.usAverage = courseAverageAgg.cached_value
                except:
                    pass
            items = []
            standards_category = Category.objects.get(name="Standards") # save time, move to top and do this once?
            for mark in Mark.objects.filter(item__category=standards_category, item__course=course,
                                            item__marking_period=marking_period,
                                            student=student, description="Session"):
                markItem = struct()
                markItem.name = mark.item.name
                markItem.range = ''
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
        #GAHH ALL (faux) SPRUCING AT THE END
        us_averages = {}
        for a in averages:
            if denominators[a] > 0:
                us_averages[a] = averages[a] / denominators[a] # keep precision for gpa calculation
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
                if us_averages[gA] is not None:
                    session_gpa += us_averages[gA]
                    i += 1
            except:
                pass

        if i > 0:
            student.session_gpa = Decimal(str(session_gpa / i)).quantize(Decimal(str(0.01)))
            # eventually remove this check and don't do any GPA calculation in this function
            discrepancy = student.session_gpa - student.calculate_gpa_mp(marking_period)
            if discrepancy:
                print 'BADNESS! GPA calculation problem for', student, marking_period, discrepancy
        
        # Cannot just rely on student.gpa for the cumulative GPA; it does not reflect report's date
        student.current_report_cumulative_gpa = student.calculate_gpa(for_date)

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
    #return pod_save(filename, ".pdf", data, template)
    return pod_save(filename, "." + str(format), data, template)
