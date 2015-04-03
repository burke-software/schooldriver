# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Max
from django.utils.text import slugify

from ecwsp.sis.models import SchoolYear, Student
from ecwsp.work_study.models import StudentWorker
from ecwsp.sis.uno_report import uno_save
from ecwsp.schedule.models import MarkingPeriod, CourseSection
from ecwsp.grades.models import StudentMarkingPeriodGrade
from ecwsp.benchmark_grade.models import (
    Category, Item, Aggregate, Demonstration, CalculationRulePerCourseCategory)
from ecwsp.benchmark_grade.utility import benchmark_find_calculation_rule, gradebook_get_average
from ecwsp.benchmark_grade.views import gradebook

import tempfile
import os

if 'TRAVIS' not in os.environ:
    """this import is killing us on TravisCI, so I'm removing it. There
    may be a better way to do this, but we honestly don't need anything
    from this file during our test runs."""
    import uno

import re
from decimal import Decimal, ROUND_HALF_UP
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


def get_benchmark_report_card_data(report_context, appy_context, students):
    PASSING_GRADE = 3 # TODO: pull config value. Roche has it set to something crazy now and I don't want to deal with it
    data = appy_context
    for_date = report_context['date_end']
    try: omit_substitutions = report_context['omit_substitutions']
    except KeyError: omit_substitutions = False
    school_year = SchoolYear.objects.filter(start_date__lt=for_date).order_by('-start_date')[0]
    calculation_rule = benchmark_find_calculation_rule(school_year)
    attendance_marking_periods = MarkingPeriod.objects.filter(school_year=school_year,
                                                  start_date__lt=for_date,
                                                  show_reports=True)
    marking_period = attendance_marking_periods.order_by('-start_date')[0]
    for student in students:
        # Backwards compatibility for existing templates
        student.fname = student.first_name
        student.lname = student.last_name

        student.year_course_sections = CourseSection.objects.filter(
            courseenrollment__user=student,
            course__graded=True,
            marking_period__school_year=school_year,
        ).distinct().order_by('course__department')
        student.course_sections = []
        student.count_total_by_category_name = {}
        student.count_missing_by_category_name = {}
        student.count_passing_by_category_name = {}
        for course_section in student.year_course_sections:
            course_section.average = gradebook_get_average(student, course_section, None, marking_period, None, omit_substitutions = omit_substitutions)
            course_section.current_marking_periods = course_section.marking_period.filter(start_date__lt=for_date).order_by('start_date')
            course_section.categories = Category.objects.filter(item__course_section=course_section, item__mark__student=student).distinct()
            course_section.category_by_name = {}
            for category in course_section.categories:
                try:
                    category.weight_percentage = calculation_rule.per_course_category_set.get(category=category, apply_to_departments=course_section.department).weight * Decimal(100)
                except CalculationRulePerCourseCategory.DoesNotExist:
                    category.weight_percentage = Decimal(0)
                category.weight_percentage = category.weight_percentage.quantize(Decimal('0'), ROUND_HALF_UP)
                category.overall_count_total = 0
                category.overall_count_missing = 0
                category.overall_count_passing = 0
                for course_section_marking_period in course_section.current_marking_periods:
                    course_section_marking_period.category = category
                    course_section_marking_period.category.average = gradebook_get_average(student, course_section, category, course_section_marking_period, None, omit_substitutions = omit_substitutions)
                    items = Item.objects.filter(course_section=course_section, marking_period=course_section_marking_period, category=category, mark__student=student).annotate(best_mark=Max('mark__mark')).exclude(best_mark=None)
                    course_section_marking_period.category.count_total = items.exclude(best_mark=None).distinct().count()
                    course_section_marking_period.category.count_missing = items.filter(best_mark__lt=PASSING_GRADE).distinct().count()
                    course_section_marking_period.category.count_passing = items.filter(best_mark__gte=PASSING_GRADE).distinct().count()
                    if course_section_marking_period.category.count_total:
                        course_section_marking_period.category.count_percentage = (Decimal(course_section_marking_period.category.count_passing) / course_section_marking_period.category.count_total * 100).quantize(Decimal('0', ROUND_HALF_UP))

                    # TODO: We assume here that flagging something visually means it's "missing." This should be done in a better way that's not opaque to users.
                    if not calculation_rule.substitution_set.filter(apply_to_departments=course_section.department, flag_visually=True).exists():
                        course_section_marking_period.category.count_passing = course_section_marking_period.category.count_total
                        course_section_marking_period.category.count_missing = 0
                        course_section_marking_period.category.count_percentage = 100

                    category.overall_count_total += course_section_marking_period.category.count_total
                    category.overall_count_missing += course_section_marking_period.category.count_missing
                    category.overall_count_passing += course_section_marking_period.category.count_passing

                    item_names = items.values_list('name').distinct()
                    course_section_marking_period.category.item_groups = []
                    for item_name_tuple in item_names:
                        item_name = item_name_tuple[0]
                        item_group = struct()
                        item_group.name = item_name
                        item_group.items = items.filter(name=item_name).distinct()
                        course_section_marking_period.category.item_groups.append(item_group)

                    course_section_marking_period.category_by_name = getattr(course_section_marking_period, 'category_by_name', {})
                    # make a copy so we don't overwrite the last marking period's data
                    course_section_marking_period.category_by_name[category.name] = copy.copy(course_section_marking_period.category)
                    # the last time through the loop is the most current marking period,
                    # so give that to anyone who doesn't request an explicit marking period
                    #category = course_marking_period.category

                course_section.category_by_name[category.name] = category
                if category.overall_count_total:
                    category.overall_count_percentage = (Decimal(category.overall_count_passing) / category.overall_count_total * 100).quantize(Decimal('0', ROUND_HALF_UP))
                student.count_total_by_category_name[category.name] = student.count_total_by_category_name.get(category.name, 0) + category.overall_count_total
                student.count_missing_by_category_name[category.name] = student.count_missing_by_category_name.get(category.name, 0) + category.overall_count_missing
                student.count_passing_by_category_name[category.name] = student.count_passing_by_category_name.get(category.name, 0) + category.overall_count_passing

            # some components of report need access to course sections for entire year (student.year_course_sections)
            # but we must keep student.course_sections restricted to the current marking period for compatibility
            if marking_period in course_section.marking_period.all():
                student.course_sections.append(course_section)

        student.count_percentage_by_category_name = {}
        for category_name, value in student.count_total_by_category_name.items():
            if value:
                student.count_percentage_by_category_name[category_name] = (Decimal(student.count_passing_by_category_name[category_name]) / value * 100).quantize(Decimal('0', ROUND_HALF_UP))

        # make categories available

        try:
            student.session_gpa = student.studentmarkingperiodgrade_set.get(
                marking_period=marking_period).grade
        except StudentMarkingPeriodGrade.DoesNotExist:
            student.session_gpa = None
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

@staff_member_required
def student_incomplete_course_sections(request):
    if 'inverse' in request.GET:
        inverse = True
    else:
        inverse = False

    from ecwsp.sis.xl_report import XlReport
    from ecwsp.work_study.models import StudentWorker

    AGGREGATE_CRITERIA = {'category__name': 'Standards', 'cached_substitution': 'INC'}

    #school_year = SchoolYear.objects.filter(start_date__lt=date.today()).order_by('-start_date')[0]
    school_year = SchoolYear.objects.get(active_year=True)
    '''
    if inverse:
        method = Student.objects.exclude
    else:
        method = Student.objects.filter
    students = method(aggregate__in=Aggregate.objects.filter(course__marking_period__school_year=school_year, **AGGREGATE_CRITERIA).distinct()).distinct()
    students = students.filter(inactive=False).order_by('year', 'lname', 'fname')
    '''
    students = Student.objects.filter(is_active=True).order_by('year', 'last_name', 'first_name')
    data = []
    titles = ['Last Name', 'First Name', 'Year', 'Work Day', 'Incomplete Course Sections']
    for student in students:
        aggs = Aggregate.objects.filter(student=student, marking_period__school_year=school_year, **AGGREGATE_CRITERIA).distinct().order_by('marking_period__start_date')
        # make sure the student is actually enrolled in these course sections
        aggs = aggs.filter(course_section__courseenrollment__user=student)
        if inverse and aggs.count():
            continue
        if not inverse and not aggs.count():
            continue
        try:
            work_day = StudentWorker.objects.get(username=student.username).day
        except StudentWorker.DoesNotExist:
            work_day = None
        course_section_details = {}
        for agg in aggs:
            course_section_detail = course_section_details.get(agg.course_section_id, {})
            course_section_detail['name'] = agg.course_section.name
            marking_periods = course_section_detail.get('marking_periods', [])
            marking_periods.append(agg.marking_period.shortname)
            course_section_detail['marking_periods'] = marking_periods
            course_section_details[agg.course_section_id] = course_section_detail
        narrative = []
        course_section_details = sorted(course_section_details.items(), key=lambda(k, v): (v, k))
        for course_section_detail in course_section_details:
            course_section_detail = course_section_detail[1] # discard the course section id
            narrative.append(u'{} ({})'.format(course_section_detail['name'], u', '.join(course_section_detail['marking_periods'])))
        data.append([student.last_name, student.first_name, student.year, work_day, u'; '.join(narrative)])

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
    COURSE_SECTION_THRESHOLD = 3
    return count_items_by_category_across_course_sections(YEAR_CATEGORY_NAMES, CURRENT_MARKING_PERIOD_CATEGORY_NAMES, ITEM_CRITERIA, CATEGORY_HEADING_FORMAT, PERCENTAGE_THRESHOLD, COURSE_SECTION_THRESHOLD, inverse)

def count_items_by_category_across_course_sections(year_category_names, current_marking_period_category_names, item_criteria, category_heading_format, percentage_threshold, course_section_threshold, inverse=False):
    from ecwsp.sis.xl_report import XlReport
    from ecwsp.work_study.models import StudentWorker

    all_category_names = list(year_category_names)
    all_category_names.extend(current_marking_period_category_names)
    all_categories = Category.objects.filter(name__in=all_category_names)
    year_categories = Category.objects.filter(name__in=year_category_names)
    current_marking_period_categories = Category.objects.filter(name__in=current_marking_period_category_names)
    titles = ['Last Name', 'First Name', 'Year', 'Work Day']
    if not inverse:
        titles.append('Course Section')
        for c in all_categories: titles.append(category_heading_format.format(c.name))
    #school_year = SchoolYear.objects.filter(start_date__lt=date.today()).order_by('-start_date')[0]
    school_year = SchoolYear.objects.get(active_year=True)
    marking_period = school_year.markingperiod_set.filter(show_reports=True, start_date__lt=date.today()).order_by('-start_date')[0]

    data = []
    for student in Student.objects.filter(is_active=True).order_by('year', 'last_name', 'first_name'):
        try:
            work_day = StudentWorker.objects.get(username=student.username).day
        except StudentWorker.DoesNotExist:
            work_day = None
        matching_course_sections = []
        for course_section in student.coursesection_set.filter(marking_period__school_year=school_year).distinct():
            items = Item.objects.filter(Q(category__in=current_marking_period_categories, marking_period=marking_period) | Q(category__in=year_categories),
                                        course_section=course_section, mark__student=student).annotate(best_mark=Max('mark__mark')).exclude(best_mark=None)
            total_item_count = items.count()
            if not total_item_count:
                continue

            course_section_match = False
            matching_course_section_detail = [course_section.name]
            # check for combined category matches
            matching_item_count = items.filter(**item_criteria).count()
            matching_percentage = round(float(matching_item_count) / total_item_count * 100, 0)
            if matching_percentage >= percentage_threshold:
                course_section_match = True
            for c in all_categories:
                # check for individual category matches, and get detail for each category if combined matched already
                total_items_in_category = items.filter(category=c).count()
                matching_items_in_category = items.filter(**item_criteria).filter(category=c).count()
                if total_items_in_category:
                    matching_percentage_in_category = round(float(matching_items_in_category) / total_items_in_category * 100)
                else:
                    matching_percentage_in_category = 0
                matching_course_section_detail.append('{}/{} ({}%)'.format(matching_items_in_category, total_items_in_category, matching_percentage_in_category))
                if matching_percentage_in_category >= percentage_threshold:
                    course_section_match = True
            if course_section_match:
                matching_course_sections.append(matching_course_section_detail)

        if len(matching_course_sections) >= course_section_threshold:
            if not inverse:
                for course_section in matching_course_sections:
                    row = [student.last_name, student.first_name, student.year, work_day]
                    row.extend(course_section)
                    data.append(row)
        elif inverse:
            row = [student.last_name, student.first_name, student.year, work_day]
            data.append(row)
    report = XlReport()
    report.add_sheet(data, header_row=titles, heading="Sheet1", auto_width=True)
    return report.as_download()

@staff_member_required
def gradebook_export(request, course_section_id):
    gradebook_data = gradebook(request, course_section_id, for_export=True)
    if type(gradebook_data) is not dict:
        # something we can't use, like a 404 or a redirect
        return gradebook_data

    from ecwsp.sis.xl_report import XlReport
    report = XlReport(file_name=slugify(gradebook_data['course_section'].name))
    rows = []
    item_attributes = (
        'category',
        'name',
        'marking_period',
        'assignment_type',
        'benchmark',
        'date',
        'points_possible',
        'description',
    )
    demonstration_attributes = (
        'name',
    )
    row_counter = 0
    # explain all the header rows in the first column
    for attribute in item_attributes:
        rows.append([Item._meta.get_field(attribute).verbose_name.title()])
        row_counter += 1
    for attribute in demonstration_attributes:
        rows.append([u'Demonstration ' + Demonstration._meta.get_field(attribute).verbose_name.title()])
        row_counter += 1
    # then list all the students in the first column
    for student in gradebook_data['students']:
        rows.append([student])
    # fill in the column headers, with column one per item/demonstration
    for item in gradebook_data['items']:
        if item.demonstration_set.count():
            for dem in item.demonstration_set.all():
                row_counter = 0
                for attribute in item_attributes:
                    rows[row_counter].append(getattr(item, attribute))
                    row_counter += 1
                for attribute in demonstration_attributes:
                    rows[row_counter].append(getattr(dem, attribute))
                    row_counter += 1
        else:
            row_counter = 0
            for attribute in item_attributes:
                rows[row_counter].append(getattr(item, attribute))
                row_counter += 1
            for attribute in demonstration_attributes:
                rows[row_counter].append('---------')
                row_counter += 1
    # maybe attributes will be user-configurable in the future?
    if not row_counter:
        rows.append([])
        row_counter = 1
    # add one-off label to the bottom header row of the last column
    rows[row_counter - 1].append('Course Section Average')
    # save coordinates for formatting later
    course_section_average_row = row_counter - 1
    course_section_average_column = len(rows[row_counter - 1]) - 1
    # actually write out the students' grades
    for student in gradebook_data['students']:
        for mark in student.marks:
            rows[row_counter].append(mark.get_grade())
        rows[row_counter].append(student.average)
        row_counter += 1

    report.add_sheet(rows, title=gradebook_data['course_section'].name)
    sheet = report.workbook.get_active_sheet()
    if report.old_openpyxl:
        for row_number in range(0, len(item_attributes) + len(demonstration_attributes)):
            sheet.cell(row=row_number, column=0).style.font.bold = True
        sheet.cell(row=course_section_average_row, column=course_section_average_column).style.font.bold = True
    else:
        for row_number in range(1, len(item_attributes) + len(demonstration_attributes)):
            cell = sheet.cell(row=row_number, column=1)
            cell.style = cell.style.copy(font=cell.style.font.copy(bold=True))
        cell = sheet.cell(row=course_section_average_row, column=course_section_average_column)
        cell.style = cell.style.copy(font=cell.style.font.copy(bold=True))
    return report.as_download()
