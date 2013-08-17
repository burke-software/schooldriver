# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

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
import copy

class struct(object):
    def __unicode__(self):
        return ""

def draw_gauge(percentage, width=10, filled_char=u'█', empty_char=u'░'):
    ''' creates a string with unicode box drawing characters to represent percentage visually '''
    percentage /= Decimal(100)
    filled = int(Decimal(width * percentage).quantize(Decimal('0')))
    if filled > width: filled = width
    elif filled < 0: filled = 0
    output = filled_char * filled
    output += empty_char * (width - filled)
    return output


def benchmark_report_card(grade_template_report, template, options, students, format="odt"):
    PASSING_GRADE = 3 # TODO: pull config value. Roche has it set to something crazy now and I don't want to deal with it
    data = grade_template_report.data
    for_date = grade_template_report.for_date
    try: omit_substitutions = options['omit_substitutions']
    except KeyError: omit_substitutions = False
    school_year = SchoolYear.objects.filter(start_date__lt=for_date).order_by('-start_date')[0]
    calculation_rule = benchmark_find_calculation_rule(school_year)
    attendance_marking_periods = MarkingPeriod.objects.filter(school_year=school_year,
                                                  start_date__lt=for_date,
                                                  show_reports=True)
    marking_period = attendance_marking_periods.order_by('-start_date')[0]
    for student in students:
        student.year_courses = Course.objects.filter(
            courseenrollment__user=student,
            graded=True,
            marking_period__school_year=school_year,
        ).distinct().order_by('department')
        student.courses = []
        student.count_total_by_category_name = {}
        student.count_missing_by_category_name = {}
        student.count_passing_by_category_name = {}
        for course in student.year_courses:
            course.average = gradebook_get_average(student, course, None, marking_period, None, omit_substitutions = omit_substitutions)
            course.current_marking_periods = course.marking_period.filter(start_date__lt=for_date).order_by('start_date')
            course.categories = Category.objects.filter(item__course=course, item__mark__student=student).distinct()
            course.category_by_name = {}
            for category in course.categories:
                try:
                    category.weight_percentage = calculation_rule.per_course_category_set.get(category=category, apply_to_departments=course.department).weight * Decimal(100)
                except CalculationRulePerCourseCategory.DoesNotExist:
                    category.weight_percentage = Decimal(0)
                category.weight_percentage = category.weight_percentage.quantize(Decimal('0'), ROUND_HALF_UP)
                category.overall_count_total = 0
                category.overall_count_missing = 0
                category.overall_count_passing = 0
                for course_marking_period in course.current_marking_periods:
                    course_marking_period.category = category
                    course_marking_period.category.average = gradebook_get_average(student, course, category, course_marking_period, None, omit_substitutions = omit_substitutions)
                    items = Item.objects.filter(course=course, marking_period=course_marking_period, category=category, mark__student=student).annotate(best_mark=Max('mark__mark')).exclude(best_mark=None)
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
                    # make a copy so we don't overwrite the last marking period's data
                    course_marking_period.category_by_name[category.name] = copy.copy(course_marking_period.category)
                    # the last time through the loop is the most current marking period,
                    # so give that to anyone who doesn't request an explicit marking period
                    #category = course_marking_period.category

                course.category_by_name[category.name] = category
                if category.overall_count_total:
                    category.overall_count_percentage = (Decimal(category.overall_count_passing) / category.overall_count_total * 100).quantize(Decimal('0', ROUND_HALF_UP))
                student.count_total_by_category_name[category.name] = student.count_total_by_category_name.get(category.name, 0) + category.overall_count_total
                student.count_missing_by_category_name[category.name] = student.count_missing_by_category_name.get(category.name, 0) + category.overall_count_missing
                student.count_passing_by_category_name[category.name] = student.count_passing_by_category_name.get(category.name, 0) + category.overall_count_passing

            # some components of report need access to courses for entire year (student.year_courses)
            # but we must keep student.courses restricted to the current marking period for compatibility
            if marking_period in course.marking_period.all():
                student.courses.append(course)

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
    data['draw_gauge'] = draw_gauge
    return grade_template_report.pod_save(template)

@staff_member_required
def student_incomplete_courses(request):
    if 'inverse' in request.GET: 
        inverse = True
    else:
        inverse = False

    from ecwsp.sis.xl_report import XlReport
    from ecwsp.work_study.models import StudentWorker

    AGGREGATE_CRITERIA = {'category__name': 'Standards', 'cached_substitution': 'INC'}

    school_year = SchoolYear.objects.filter(start_date__lt=date.today()).order_by('-start_date')[0]
    '''
    if inverse:
        method = Student.objects.exclude
    else:
        method = Student.objects.filter
    students = method(aggregate__in=Aggregate.objects.filter(course__marking_period__school_year=school_year, **AGGREGATE_CRITERIA).distinct()).distinct()
    students = students.filter(inactive=False).order_by('year', 'lname', 'fname')
    '''
    students = Student.objects.filter(inactive=False).order_by('year', 'lname', 'fname')
    data = []
    titles = ['Last Name', 'First Name', 'Year', 'Work Day', 'Incomplete Courses']
    for student in students:
        aggs = Aggregate.objects.filter(student=student, marking_period__school_year=school_year, **AGGREGATE_CRITERIA).distinct().order_by('marking_period__start_date')
        # make sure the student is actually enrolled in these courses
        aggs = aggs.filter(course__in=student.courseenrollment_set.values_list('course'))
        if inverse and aggs.count():
            continue
        if not inverse and not aggs.count():
            continue
        try:
            work_day = StudentWorker.objects.get(username=student.username).day
        except StudentWorker.DoesNotExist:
            work_day = None
        course_details = {}
        for agg in aggs:
            course_detail = course_details.get(agg.course_id, {})
            course_detail['fullname'] = agg.course.fullname
            marking_periods = course_detail.get('marking_periods', [])
            marking_periods.append(agg.marking_period.shortname)
            course_detail['marking_periods'] = marking_periods
            course_details[agg.course_id] = course_detail
        narrative = []
        course_details = sorted(course_details.items(), key=lambda(k, v): (v, k))
        for course_detail in course_details:
            course_detail = course_detail[1] # discard the course id
            narrative.append(u'{} ({})'.format(course_detail['fullname'], u', '.join(course_detail['marking_periods'])))
        data.append([student.lname, student.fname, student.year, work_day, u'; '.join(narrative)])
    
    report = XlReport()
    report.add_sheet(data, header_row=titles, title="Sheet1", auto_width=True)
    return report.as_download()  

@staff_member_required
def student_zero_dp_standards(request):
    if 'inverse' in request.GET: 
        inverse = True
    else:
        inverse = False

    YEAR_CATEGORY_NAMES = ('Standards',)
    CURRENT_MARKING_PERIOD_CATEGORY_NAMES = ('Daily Practice',)
    ITEM_CRITERIA = {'best_mark': 0}
    CATEGORY_HEADING_FORMAT = '{} at 0'
    PERCENTAGE_THRESHOLD = 20
    COURSE_THRESHOLD = 3
    return count_items_by_category_across_courses(YEAR_CATEGORY_NAMES, CURRENT_MARKING_PERIOD_CATEGORY_NAMES, ITEM_CRITERIA, CATEGORY_HEADING_FORMAT, PERCENTAGE_THRESHOLD, COURSE_THRESHOLD, inverse)

def count_items_by_category_across_courses(year_category_names, current_marking_period_category_names, item_criteria, category_heading_format, percentage_threshold, course_threshold, inverse=False):
    from ecwsp.sis.xl_report import XlReport
    from ecwsp.work_study.models import StudentWorker

    all_category_names = list(year_category_names)
    all_category_names.extend(current_marking_period_category_names)
    all_categories = Category.objects.filter(name__in=all_category_names)
    year_categories = Category.objects.filter(name__in=year_category_names)
    current_marking_period_categories = Category.objects.filter(name__in=current_marking_period_category_names)
    titles = ['Last Name', 'First Name', 'Year', 'Work Day']
    if not inverse:
        titles.append('Course')
        for c in all_categories: titles.append(category_heading_format.format(c.name))
    school_year = SchoolYear.objects.filter(start_date__lt=date.today()).order_by('-start_date')[0]
    marking_period = school_year.markingperiod_set.filter(show_reports=True, start_date__lt=date.today()).order_by('-start_date')[0]

    data = []
    for student in Student.objects.filter(inactive=False).order_by('year', 'lname', 'fname'):
        try:
            work_day = StudentWorker.objects.get(username=student.username).day
        except StudentWorker.DoesNotExist:
            work_day = None
        matching_courses = []
        for course in student.course_set.filter(marking_period__school_year=school_year).distinct():
            items = Item.objects.filter(Q(category__in=current_marking_period_categories, marking_period=marking_period) | Q(category__in=year_categories),
                                        course=course, mark__student=student).annotate(best_mark=Max('mark__mark')).exclude(best_mark=None)
            total_item_count = items.count()
            if not total_item_count:
                continue

            course_match = False
            matching_course_detail = [course.fullname]
            # check for combined category matches
            matching_item_count = items.filter(**item_criteria).count()
            matching_percentage = round(float(matching_item_count) / total_item_count * 100, 0)
            if matching_percentage >= percentage_threshold:
                course_match = True
            for c in all_categories:
                # check for individual category matches, and get detail for each category if combined matched already
                total_items_in_category = items.filter(category=c).count()
                matching_items_in_category = items.filter(**item_criteria).filter(category=c).count()
                if total_items_in_category:
                    matching_percentage_in_category = round(float(matching_items_in_category) / total_items_in_category * 100)
                else:
                    matching_percentage_in_category = 0
                matching_course_detail.append('{}/{} ({}%)'.format(matching_items_in_category, total_items_in_category, matching_percentage_in_category))
                if matching_percentage_in_category >= percentage_threshold:
                    course_match = True
            if course_match:
                matching_courses.append(matching_course_detail)

        if len(matching_courses) >= course_threshold:
            if not inverse:
                for course in matching_courses:
                    row = [student.lname, student.fname, student.year, work_day]
                    row.extend(course)
                    data.append(row)
        elif inverse:
            row = [student.lname, student.fname, student.year, work_day]
            data.append(row)
    report = XlReport()
    report.add_sheet(data, header_row=titles, heading="Sheet1", auto_width=True)
    return report.as_download()
